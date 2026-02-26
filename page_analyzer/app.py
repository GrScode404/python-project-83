from flask import Flask, render_template

from page_analyzer.db import get_connection

app = Flask(__name__)  # NOSONAR


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test-db')
def test_db():
    conn = get_connection()
    conn.close()
    return "DB OK"
