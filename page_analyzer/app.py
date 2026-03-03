import os
from datetime import datetime

import requests
import validators
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

from page_analyzer import db
from page_analyzer.parser import extract_page_data
from page_analyzer.url_normalizer import normalize_url

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

    try:
        is_valid = validators.url(url)
    except Exception:
        is_valid = False

    if is_valid is not True:
        flash('Некорректный URL', 'danger')
        return render_template('index.html'), 422

    normalized_url = normalize_url(url)

    existing = db.url_exists(normalized_url)
    if existing:
        url_id = existing['id']
        flash('Страница уже существует', 'info')
    else:
        url_id = db.create_url(normalized_url, datetime.now())
        flash('Страница успешно добавлена', 'success')

    return redirect(url_for('show_url', id=url_id))


@app.get('/urls/<int:id>')
def show_url(id):
    url = db.get_url(id)
    if not url:
        abort(404)
    
    checks = db.get_url_checks(id)
    return render_template('url.html', url=url, checks=checks)


@app.get('/urls')
def urls():
    all_urls = db.get_all_urls()
    return render_template('urls.html', urls=all_urls)


@app.post('/urls/<int:id>/checks')
def check_url(id):
    url_data = db.get_url(id)
    if not url_data:
        abort(404)

    url = url_data['name']

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        page_data = extract_page_data(response)
    except RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('show_url', id=id))
    
    db.create_check(
        url_id=id,
        status_code=page_data['status_code'],
        h1=page_data['h1'],
        title=page_data['title'],
        description=page_data['description'],
        created_at=datetime.now()
    )
    
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('show_url', id=id))


