import os
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from flask import Flask, jsonify, render_template, request
from google.cloud import firestore
from firebase_config import get_db

app = Flask(__name__)
COLLECTIONS = {'rooms', 'guests', 'reservations'}
ACTIVE = {'Pending', 'Confirmed', 'Checked-in'}
STATUSES = ACTIVE | {'Checked-out', 'Cancelled'}

class Problem(Exception):
    def __init__(self, message, status=400):
        self.message, self.status = message, status

@app.errorhandler(Problem)
def problem(e):
    return jsonify(error=e.message), e.status

@app.errorhandler(Exception)
def unexpected(e):
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        return jsonify(error=e.description), e.code
    app.logger.exception('Request failed')
    return jsonify(error='Database or server operation failed. Check server logs.'), 500

def text(d, key, required=True):
    v = d.get(key, '')
    if not isinstance(v, str) or len(v) > 2000 or (required and not v.strip()):
        raise Problem(f'Invalid {key}')
    return v.strip()

def integer(d, key, minimum=1):
    v = d.get(key)
    if type(v) is not int or v < minimum:
        raise Problem(f'{key} must be an integer of at least {minimum}')
    return v

def money(d, key):
    try:
        v = Decimal(str(d.get(key)))
        if not v.is_finite() or not 0 < v <= 10000000: raise ValueError()
        return float(v.quantize(Decimal('0.01')))
    except (InvalidOperation, ValueError):
        raise Problem(f'Invalid {key}')

def choice(d, key, options):
    v = text(d, key)
    if v not in options: raise Problem(f'Invalid {key}')
    return v

def day(d, key):
    try: return date.fromisoformat(text(d, key))
    except ValueError: raise Problem(f'Invalid {key}')

def record(s):
    return {**s.to_dict(), 'id': s.id}

def validate(resource, d):
    if resource == 'rooms':
        return dict(room_number=text(d,'room_number'), room_type=text(d,'room_type'), floor=integer(d,'floor',0), capacity=integer(d,'capacity'), price_per_night=money(d,'price_per_night'), amenities=text(d,'amenities',False), description=text(d,'description',False), status=choice(d,'status',{'Available','Maintenance','Cleaning'}))
    if resource == 'guests':
        email=text(d,'email')
        import re
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email): raise Problem('Invalid email')
        return dict(full_name=text(d,'full_name'), email=email, contact_number=text(d,'contact_number'), address=text(d,'address'), nationality=text(d,'nationality'))
    start,end=day(d,'check_in'),day(d,'check_out')
    if end<=start: raise Problem('Check-out must be after check-in')
    return dict(room_id=text(d,'room_id'), guest_id=text(d,'guest_id'), check_in=start.isoformat(), check_out=end.isoformat(), number_of_guests=integer(d,'number_of_guests'), total_nights=(end-start).days, reservation_status=choice(d,'reservation_status',STATUSES), payment_status=choice(d,'payment_status',{'Unpaid','Paid'}), payment_method=choice(d,'payment_method',{'Cash','Card','GCash','Bank Transfer'}), special_requests=text(d,'special_requests',False))

@app.get('/')
def home(): return render_template('index.html')

@app.get('/api/health')
def health():
    list(get_db().collection('rooms').limit(1).stream())
    return jsonify(connected=True)

@app.route('/api/<resource>', methods=['GET','POST'])
@app.route('/api/<resource>/<rid>', methods=['GET','PUT','DELETE'])
def crud(resource,rid=None):
    if resource not in COLLECTIONS: raise Problem('Unknown collection',404)
    db=get_db(); col=db.collection(resource)
    if request.method=='GET':
        if rid:
            s=col.document(rid).get()
            if not s.exists: raise Problem('Record not found',404)
            return jsonify(record(s))
        q=request.args.get('q','').casefold(); status=request.args.get('status','')
        rows=[record(s) for s in col.stream()]
        return jsonify([r for r in rows if (not q or q in str(r).casefold()) and (not status or status==r.get('reservation_status',r.get('status')))])
    ref=col.document(rid) if rid else col.document()
    data=None
    if request.method!='DELETE':
        raw=request.get_json(silent=True)
        if not isinstance(raw,dict): raise Problem('JSON object required')
        data=validate(resource,raw)
    # Shared transaction guard serializes all writes, including reference checks.
    guard=db.collection('_system').document('write_guard')
    @firestore.transactional
    def mutate(tx):
        guard.get(transaction=tx)
        old=ref.get(transaction=tx)
        if rid and not old.exists: raise Problem('Record not found',404)
        reservations=[record(s) for s in db.collection('reservations').stream(transaction=tx)]
        linked=[r for r in reservations if r.get('room_id' if resource=='rooms' else 'guest_id')==ref.id] if resource!='reservations' else []
        if request.method=='DELETE':
            if linked: raise Problem('Remove linked reservations first',409)
            tx.delete(ref)
        else:
            if resource=='rooms':
                if any(s.id!=ref.id and s.to_dict().get('room_number')==data['room_number'] for s in col.stream(transaction=tx)): raise Problem('Room number already exists',409)
                if any(r['reservation_status'] in ACTIVE and (data['status']!='Available' or r['number_of_guests']>data['capacity']) for r in linked): raise Problem('Room has incompatible active reservations',409)
            if resource=='reservations':
                room=db.collection('rooms').document(data['room_id']).get(transaction=tx)
                guest=db.collection('guests').document(data['guest_id']).get(transaction=tx)
                if not room.exists or not guest.exists: raise Problem('Select an existing room and guest')
                rm=room.to_dict()
                if data['number_of_guests']>rm['capacity']: raise Problem('Room capacity exceeded')
                if data['reservation_status'] in ACTIVE:
                    if rm['status']!='Available': raise Problem('Room unavailable',409)
                    for r in reservations:
                        if r['id']!=ref.id and r['room_id']==room.id and r['reservation_status'] in ACTIVE and data['check_in']<r['check_out'] and data['check_out']>r['check_in']:
                            raise Problem('Room already booked for these dates',409)
                previous=old.to_dict() if old.exists else {}
                rate=previous.get('price_per_night',rm['price_per_night']) if previous.get('room_id')==room.id else rm['price_per_night']
                data['price_per_night']=rate
                data['total_amount']=round(rate*data['total_nights'],2)
            data[{'rooms':'room_id','guests':'guest_id','reservations':'reservation_id'}[resource]]=ref.id
            data['updated_at']=datetime.now(timezone.utc)
            if not old.exists: data['created_at']=data['updated_at']
            tx.set(ref,data,merge=old.exists)
        tx.set(guard,{'updated_at':firestore.SERVER_TIMESTAMP})
    mutate(db.transaction())
    if request.method=='DELETE': return jsonify(message='Record deleted')
    return jsonify(record(ref.get())), 200 if rid else 201

if __name__=='__main__':
    app.run(host='127.0.0.1',port=int(os.getenv('PORT','5000')),debug=False)
