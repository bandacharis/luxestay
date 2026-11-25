import os
from pathlib import Path
from functools import lru_cache
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
BASE=Path(__file__).resolve().parent
load_dotenv(BASE/'.env')
@lru_cache(maxsize=1)
def get_db():
    path=Path(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    if not path.is_absolute(): path=BASE/path
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.Certificate(str(path)))
    return firestore.client()
