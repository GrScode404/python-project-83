import os
from datetime import datetime
from typing import Optional

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не установлена!")


def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def url_exists(url: str) -> Optional[dict]:

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT id FROM urls WHERE name = %s',
                (url,)
            )
            return cur.fetchone()


def create_url(url: str, created_at: datetime) -> int:

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO urls (name, created_at)
                VALUES (%s, %s)
                RETURNING id
                """,
                (url, created_at)
            )
            url_id = cur.fetchone()['id']
            conn.commit()
            return url_id


def get_url(url_id: int) -> Optional[dict]:

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT id, name, created_at FROM urls WHERE id = %s',
                (url_id,)
            )
            return cur.fetchone()


def get_url_checks(url_id: int) -> list:

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, status_code, h1, title, description, created_at
                FROM url_checks
                WHERE url_id = %s
                ORDER BY id DESC;
                """,
                (url_id,),
            )
            return cur.fetchall()


def get_all_urls() -> list:

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    urls.id,
                    urls.name,
                    uc.status_code,
                    uc.created_at
                FROM urls
                LEFT JOIN LATERAL (
                    SELECT status_code, created_at
                    FROM url_checks
                    WHERE url_checks.url_id = urls.id
                    ORDER BY created_at DESC
                    LIMIT 1
                ) uc ON true
                ORDER BY urls.id DESC;
                """
            )
            return cur.fetchall()


def create_check(
    url_id: int,
    status_code: int,
    h1: Optional[str],
    title: Optional[str],
    description: Optional[str],
    created_at: datetime
) -> int:

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO url_checks (
                    url_id, 
                    status_code, 
                    h1, 
                    title, 
                    description, 
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (
                    url_id,
                    status_code,
                    h1,
                    title,
                    description,
                    created_at
                )
            )
            check_id = cur.fetchone()['id']
            conn.commit()
            return check_id