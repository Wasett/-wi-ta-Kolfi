from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import os
import psycopg2
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = 'supersecretkey123'

# ---------------- Dane uczestników ----------------
participants = [
    {'id': 1, 'name': 'Ola'},
    {'id': 2, 'name': 'Seba'},
    {'id': 3, 'name': 'Sylwek'},
    {'id': 4, 'name': 'Sylwia'},
    {'id': 5, 'name': 'Martyna'},
    {'id': 6, 'name': 'Agnieszka'},
    {'id': 7, 'name': 'Mariusz'},
    {'id': 8, 'name': 'Jasia'},
    {'id': 9, 'name': 'Gosia'},
    {'id': 10, 'name': 'Danuta'},
    {'id': 11, 'name': 'Jarek'},
    {'id': 12, 'name': 'Lidia'},
    {'id': 13, 'name': 'Bartek'},
    {'id': 14, 'name': 'Monika'}
]

# ---------------- Dane administratora ----------------
ADMIN_LOGIN = 'seba'
ADMIN_PASSWORD = 'jestok'


# ---------------- Konfiguracja bazy PostgreSQL ----------------
DATABASE_URL = os.getenv('DATABASE_URL')

def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS results (
            participant_id INTEGER PRIMARY KEY,
            drawn_name TEXT
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

def load_results():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT participant_id, drawn_name FROM results')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    results = {pid: name for pid, name in rows}
    already_drawn = set(results.keys())
    return results, already_drawn

def save_result(participant_id, drawn_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO results (participant_id, drawn_name)
        VALUES (%s, %s)
        ON CONFLICT (participant_id) DO UPDATE
        SET drawn_name = EXCLUDED.drawn_name
    ''', (participant_id, drawn_name))
    conn.commit()
    cur.close()
    conn.close()

def clear_results():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM results')
    conn.commit()
    cur.close()
    conn.close()


# ---------------- Inicjalizacja przy starcie ----------------
init_db()
results, already_drawn = load_results()


# ---------------- Strona główna ----------------
@app.route('/', methods=['GET'])
def index():
    available_participants = [p for p in participants if p['id'] not in already_drawn]
    if not available_participants:
        flash('Wszyscy uczestnicy już wylosowali swoje prezenty.')
    return render_template('index.html', participants=available_participants)


# ---------------- Losowanie ----------------
@app.route('/draw', methods=['POST'])
def draw():
    participant_id = int(request.form['participant_id'])

    if participant_id in already_drawn:
        flash('Ten uczestnik już wylosował osobę i nie może losować ponownie.')
        return redirect(url_for('index'))

    possible = [p['name'] for p in participants if p['id'] != participant_id and p['name'] not in results.values()]
    if not possible:
        flash('Brak dostępnych osób do wylosowania.')
        return redirect(url_for('index'))

    chosen_name = random.choice(possible)
    results[participant_id] = chosen_name
    already_drawn.add(participant_id)
    save_result(participant_id, chosen_name)

    return render_template('result.html', result_name=chosen_name)


# ---------------- Logowanie admina ----------------
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_LOGIN and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash('Niepoprawny login lub hasło')
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')


# ---------------- Panel admina ----------------
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        new_name = request.form['new_participant'].strip()
        if new_name:
            new_id = max([p['id'] for p in participants], default=0) + 1
            participants.append({'id': new_id, 'name': new_name})
            flash(f'Dodano uczestnika: {new_name}')
        return redirect(url_for('admin_panel'))

    display_results = []
    for p in participants:
        display_results.append({
            'name': p['name'],
            'drawn': results.get(p['id'], None)
        })

    return render_template('admin_panel.html', results=display_results)


# ---------------- Resetowanie losowania ----------------
@app.route('/admin/reset')
def admin_reset():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    results.clear()
    already_drawn.clear()
    clear_results()

    flash('Losowanie zostało zresetowane.')
    return redirect(url_for('admin_panel'))


# ---------------- Wylogowanie admina ----------------
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    flash('Wylogowano administratora.')
    return redirect(url_for('index'))


# ---------------- Uruchomienie serwera ----------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
