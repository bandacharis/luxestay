import os
import json
from pathlib import Path
from functools import lru_cache

from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore


BASE = Path(__file__).resolve().parent
load_dotenv(BASE / ".env")


@lru_cache(maxsize=1)
def get_db():

    try:
        firebase_app = firebase_admin.get_app()

    except ValueError:

        # Vercel Firebase credentials
        firebase_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")

        if firebase_json:
            service_account = json.loads(firebase_json)

            cred = credentials.Certificate(service_account)

        else:
            # Local PyCharm Firebase credentials
            key_path = os.getenv(
                "GOOGLE_APPLICATION_CREDENTIALS",
                "ServiceAccountKey.json"
            )

            path = Path(key_path)

            if not path.is_absolute():
                path = BASE / path

            if not path.is_file():
                raise FileNotFoundError(
                    f"Firebase credentials not found: {path}"
                )

            cred = credentials.Certificate(str(path))

        firebase_app = firebase_admin.initialize_app(cred)

    return firestore.client(app=firebase_app)
