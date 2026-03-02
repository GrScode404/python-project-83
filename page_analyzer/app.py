import os
from datetime import datetime
from urllib.parse import urlparse

import requests
import validators
from bs4 import BeautifulSoup
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from requests.exceptions import RequestException

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
        flash('Требуется ввести URL', 'danger')
        return render_template('index.html'), 422
    
    url = url.strip()
    
    if len(url) > 255:
        flash('URL должен быть меньше 255 символов', 'danger')
        return render_template('index.html'), 422    
    
    if not validators.url(url):
        flash('Некорректный URL', 'danger')
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
                flash('URL уже существует', 'info')
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
                flash('Страница успешно добавлена', 'success')

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
            urls = cur.fetchall()            

        return render_template('urls.html', urls=urls)


@app.post('/urls/<int:id>/checks')
def check_url(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT name FROM urls WHERE id = %s',
                (id,)
            )
            url_data = cur.fetchone()

            if not url_data:
                abort(404)

            url = url_data['name']

            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()

                hmtl = response.text
                soup = BeautifulSoup(hmtl, 'html.parser')

                h1 = soup.find('h1')
                title = soup.find('title')
                description = soup.find('meta', attrs={'name': 'description'})

                h1_text = h1.get_text(strip=True) if h1 else None
                title_text = title.get_text(strip=True) if title else None
                description_text = description['content'].strip() if description and 'content' in description.attrs else None
            
            except RequestException:
                flash('Произошла ошибка при проверке', 'danger')
                return redirect(url_for('show_url', id=id))
            
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
                    id, 
                    response.status_code, 
                    h1_text, 
                    title_text, 
                    description_text, 
                    datetime.now())                
            )
            conn.commit()
            
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('show_url', id=id))


