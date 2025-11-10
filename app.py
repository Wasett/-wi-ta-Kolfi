from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import os
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey123'

RESULTS_FILE = 'results.json'

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


# ---------------- Funkcje pomocnicze ----------------
def load_results():
    """Wczytuje wyniki z pliku JSON, jeśli istnieje i jest poprawny."""
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('results', {}), set(data.get('already_drawn', []))
        except (json.JSONDecodeError, ValueError):
            # Plik jest pusty lub uszkodzony — nadpisz pustym
            return {}, set()
    return {}, set()


def save_results(results, already_drawn):
    """Zapisuje wyniki do pliku JSON."""
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump({'results': results, 'already_drawn': list(already_drawn)}, f, ensure_ascii=False, indent=4)


# ---------------- Wczytanie danych przy starcie ----------------
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

    # Lista możliwych osób do wylosowania (bez siebie i bez już wylosowanych)
    possible = [p['name'] for p in participants if p['id'] != participant_id and p['name'] not in results.values()]
    if not possible:
        flash('Brak dostępnych osób do wylosowania.')
        return redirect(url_for('index'))

    chosen_name = random.choice(possible)
    results[participant_id] = chosen_name
    already_drawn.add(participant_id)

    # Zapisujemy wynik losowania
    save_results(results, already_drawn)

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

    # Przygotowanie danych do wyświetlenia w tabeli
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
    save_results(results, already_drawn)

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
    port = int(os.environ.get("PORT", 5000))  # Render ustawia PORT automatycznie
    app.run(host="0.0.0.0", port=port, debug=True)
