"""
LuxeStay - Bali Retreat
Automatic Firestore Sample Data Importer

Run using:
    py seed_data.py
"""

from datetime import date, timedelta
from google.cloud import firestore
from firebase_config import get_db
from app import validate, ACTIVE


# =====================================================
# 1. SAMPLE HOTEL ROOMS
# =====================================================

ROOMS = [
    ("101", "Garden Deluxe", 1, 2, 2500),
    ("102", "Coconut Standard", 1, 2, 1500),
    ("103", "Palm Terrace", 1, 3, 2800),
    ("201", "Private Pool Villa", 2, 4, 5500),
    ("202", "Ocean Breeze Suite", 2, 2, 3500),
    ("203", "Family Retreat", 2, 6, 4500),
    ("301", "Jungle Suite", 3, 2, 3800),
    ("302", "Sunset Deluxe", 3, 3, 3200),
    ("303", "Bamboo Villa", 3, 4, 4800),
    ("304", "Lotus Suite", 3, 2, 4000)
]


# =====================================================
# 2. SAMPLE HOTEL GUESTS
# =====================================================

NAMES = [
    "Maria Reyes",
    "Angela Cruz",
    "Daniel Santos",
    "Sofia Garcia",
    "Miguel Flores",
    "Isabel Ramos",
    "Gabriel Mendoza",
    "Camille Torres",
    "Andrea Lim",
    "Paolo Rivera"
]


# =====================================================
# 3. AUTOMATIC FIRESTORE DATA INSERTION
# =====================================================

def seed():

    db = get_db()

    guard = db.collection("_system").document("write_guard")

    marker = db.collection("_system").document("bali_sample_v1")

    @firestore.transactional
    def insert(tx):

        guard.get(transaction=tx)

        # Prevent duplicate sample data insertion
        if marker.get(transaction=tx).exists:

            return (
                "Sample data already imported. "
                "No changes made."
            )

        # Fetch existing Firestore records
        existing = {
            collection: {
                snapshot.id: snapshot.to_dict()

                for snapshot in db.collection(
                    collection
                ).stream(transaction=tx)
            }

            for collection in (
                "rooms",
                "guests",
                "reservations"
            )
        }

        writes = []

        for i, (
            number,
            kind,
            floor,
            capacity,
            rate
        ) in enumerate(ROOMS, 1):

            # Generate connected document IDs
            rid = f"DEMO-ROOM-{i:03d}"
            gid = f"DEMO-GUEST-{i:03d}"
            bid = f"DEMO-RES-{i:03d}"

            # Prevent overwriting existing documents
            if any(
                key in existing[collection]

                for collection, key in [
                    ("rooms", rid),
                    ("guests", gid),
                    ("reservations", bid)
                ]
            ):

                raise RuntimeError(
                    "Sample ID already exists. "
                    "Import stopped without overwriting records."
                )

            # Prevent duplicate room numbers
            if any(
                room.get("room_number") == number

                for room in existing["rooms"].values()
            ):

                raise RuntimeError(
                    f"Room {number} already exists. "
                    "Change the sample room numbers "
                    "in ROOMS and retry."
                )


            # =========================================
            # CREATE ROOM DATA
            # =========================================

            room = validate(
                "rooms",
                dict(
                    room_number=number,
                    room_type=kind,
                    floor=floor,
                    capacity=capacity,
                    price_per_night=rate,

                    amenities=(
                        "Wi-Fi, Air conditioning, "
                        "Breakfast, Garden view"
                    ),

                    description=(
                        f"Bali-inspired {kind} accommodation."
                    ),

                    status="Available"
                )
            )


            # =========================================
            # CREATE GUEST DATA
            # =========================================

            guest = validate(
                "guests",
                dict(
                    full_name=NAMES[i - 1],

                    email=f"guest{i}@example.com",

                    contact_number=f"09000000{i:03d}",

                    address="Iloilo, Philippines",

                    nationality="Filipino"
                )
            )


            # =========================================
            # GENERATE RESERVATION DATES
            # =========================================

            start = date.today() + timedelta(days=i)

            status = [
                "Confirmed",
                "Pending",
                "Confirmed",
                "Checked-in",
                "Checked-out",
                "Cancelled",
                "Confirmed",
                "Pending",
                "Confirmed",
                "Confirmed"
            ][i - 1]

            if status == "Checked-in":

                start = date.today()

            if status == "Checked-out":

                start = date.today() - timedelta(days=5)

            end = start + timedelta(days=2 + i % 3)


            # =========================================
            # CREATE RESERVATION DATA
            # =========================================

            reservation = validate(
                "reservations",
                dict(
                    room_id=rid,

                    guest_id=gid,

                    check_in=start.isoformat(),

                    check_out=end.isoformat(),

                    number_of_guests=min(capacity, 2),

                    reservation_status=status,

                    payment_status=(
                        "Paid"

                        if status in (
                            "Confirmed",
                            "Checked-in",
                            "Checked-out"
                        )

                        else "Unpaid"
                    ),

                    payment_method=(
                        "GCash" if i % 2 else "Cash"
                    ),

                    special_requests=(
                        "Extra pillows" if i % 2 else ""
                    )
                )
            )


            # =========================================
            # AUTOMATIC RESERVATION CALCULATION
            # =========================================

            reservation.update(
                price_per_night=rate,

                total_amount=round(
                    rate * reservation["total_nights"],
                    2
                )
            )


            # =========================================
            # PREPARE FIRESTORE DOCUMENTS
            # =========================================

            for collection, key, data, id_field in [

                (
                    "rooms",
                    rid,
                    room,
                    "room_id"
                ),

                (
                    "guests",
                    gid,
                    guest,
                    "guest_id"
                ),

                (
                    "reservations",
                    bid,
                    reservation,
                    "reservation_id"
                )

            ]:

                data.update({

                    id_field: key,

                    "created_at": firestore.SERVER_TIMESTAMP,

                    "updated_at": firestore.SERVER_TIMESTAMP

                })

                writes.append(

                    (
                        db.collection(
                            collection
                        ).document(key),

                        data
                    )

                )


        # =============================================
        # SAVE ALL RECORDS TO FIRESTORE
        # =============================================

        for reference, data in writes:

            tx.create(reference, data)


        # =============================================
        # UPDATE TRANSACTION GUARD
        # =============================================

        tx.set(
            guard,
            {
                "updated_at": firestore.SERVER_TIMESTAMP
            }
        )


        # =============================================
        # SAVE IMPORT MARKER
        # =============================================

        tx.create(
            marker,
            {
                "imported_at": firestore.SERVER_TIMESTAMP,

                "count": len(writes)
            }
        )

        return (
            "Success! Imported 10 rooms, "
            "10 guests and 10 reservations."
        )


    # Execute Firestore transaction
    print(insert(db.transaction()))


# =====================================================
# 4. RUN SAMPLE DATA IMPORTER
# =====================================================

if __name__ == "__main__":

    try:

        seed()

    except Exception as exc:

        raise SystemExit(
            f"Import failed: {exc}"
        )