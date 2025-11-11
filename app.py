from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import random
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey123'

# ---------------- Konfiguracja bazy ----------------
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///results.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------- Model dla wyników ----------------
class DrawResult(db.Model):
    __tablename__ = 'draw_results'
    participant_id = db.Column(db.Integer, primary_key=True)
    drawn_name = db.Column(db.String, nullable=False)

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

# ---------------- Inicjalizacja bazy ----------------
with app.app_context():
    db.create_all()

# ---------------- Funkcje pomocnicze ----------------
def get_results():
    """Pobiera wszystkie wyniki z bazy"""
    results = {}
    for row in DrawResult.query.all():
        results[row.participant_id] = row.drawn_name
    return results

def get_already_drawn():
    """Zwraca zbiór uczestników, którzy już losowali"""
    return {row.participant_id for row in DrawResult.query.all()}

# ---------------- Strona główna ----------------
@app.route('/', methods=['GET'])
def index():
    already_drawn = get_already_drawn()
    available_participants = [p for p in participants if p['id'] not in already_drawn]
    if not available_participants:
        flash('Wszyscy uczestnicy już wylosowali swoje prezenty.')
    return render_template('index.html', participants=available_participants)

# ---------------- Losowanie ----------------
@app.route('/draw', methods=['POST'])
def draw():
    participant_id = int(request.form['participant_id'])
    results = get_results()
    already_drawn = get_already_drawn()

    if participant_id in already_drawn:
        flash('Ten uczestnik już wylosował osobę i nie może losować ponownie.')
        return redirect(url_for('index'))

    possible = [p['name'] for p in participants if p['id'] != participant_id and p['name'] not in results.values()]
    if not possible:
        flash('Brak dostępnych osób do wylosowania.')
        return redirect(url_for('index'))

    chosen_name = random.choice(possible)

    # Zapis wyniku w bazie
    new_result = DrawResult(participant_id=participant_id, drawn_name=chosen_name)
    db.session.add(new_result)
    db.session.commit()

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

    results = get_results()
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

    DrawResult.query.delete()
    db.session.commit()

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
