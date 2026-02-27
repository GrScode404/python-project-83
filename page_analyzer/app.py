import os
from datetime import datetime
from urllib.parse import urlparse

import validators
from flask import Flask, flash, redirect, render_template, request, url_for

from page_analyzer.db import get_connection

app = Flask(__name__)  # NOSONAR
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # NOSONAR


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def add_url():
    url = request.form.get('url')

    if not url:
        flash('URL is required', 'danger')
        return render_template('index.html'), 422
    
    if len(url) > 255:
        flash('URL must be less than 255 characters', 'danger')
        return render_template('index.html'), 422    
    
    if not validators.url(url):
        flash('Invalid URL', 'danger')
        return render_template('index.html'), 422
    
    parsed_url = urlparse(url)
    normalized_url = f'{parsed_url.scheme}://{parsed_url.netloc}'
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT id FROM urls WHERE name = %s',
                (normalized_url,)
            )
            existing = cur.fetchone()

            if existing:
                url_id = existing['id']
                flash('URL already exists', 'info')
            else:
                cur.execute(
                    """
                    INSERT INTO urls (name, created_at)
                    VALUES (%s, %s)
                    RETURNING id
                    """,
                    (normalized_url, datetime.now())
                )
                url_id = cur.fetchone()['id']
                conn.commit()
                flash('URL added successfully', 'success')

    return redirect(url_for('show_url', id=url_id))


@app.get('/urls/<int:id>')
def show_url(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT id, name, created_at FROM urls WHERE id = %s',
                (id,)
            )
            url = cur.fetchone()

            cur.execute(
                """
                SELECT id, status_code, h1, title, description, created_at
                FROM url_checks
                WHERE url_id = %s
                ORDER BY id DESC;
                """,
                (id,),
            )
            checks = cur.fetchall()
        
        return render_template('url.html', url=url, checks=checks)


@app.get('/urls')
def urls():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT urls.id,
                    urls.name,
                    urls.created_at,
                    MAX(url_checks.created_at) AS last_check
                FROM urls
                LEFT JOIN url_checks
                    ON urls.id = url_checks.url_id
                GROUP BY urls.id
                ORDER BY urls.id DESC;
                """
            )
            urls = cur.fetchall()            

        return render_template('urls.html', urls=urls)


@app.post('/urls/<int:id>/checks')
def check_url(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO url_checks (url_id)
                VALUES (%s)
                RETURNING id;
                """,
                (id,)                
            )
            conn.commit()
            
    flash('Check started', 'success')
    return redirect(url_for('show_url', id=id))


