import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не установлена!")


def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)