from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

DATABASE = "database.db"

# Connessione database
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Creazione database automatica
def init_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS prenotazioni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            camera TEXT,
            checkin TEXT,
            checkout TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Home
@app.route('/')
def index():
    db = get_db()
    prenotazioni = db.execute("SELECT * FROM prenotazioni").fetchall()
    return render_template('index.html', prenotazioni=prenotazioni)

# Aggiungi prenotazione
@app.route('/aggiungi', methods=['POST'])
def aggiungi():
    nome = request.form['nome']
    camera = request.form['camera']
    checkin = request.form['checkin']
    checkout = request.form['checkout']

    db = get_db()
    db.execute(
        "INSERT INTO prenotazioni (nome, camera, checkin, checkout) VALUES (?, ?, ?, ?)",
        (nome, camera, checkin, checkout)
    )
    db.commit()

    return redirect('/')

# Elimina prenotazione
@app.route('/elimina/<int:id>')
def elimina(id):
    db = get_db()
    db.execute("DELETE FROM prenotazioni WHERE id = ?", (id,))
    db.commit()
    return redirect('/')

# Avvio per hosting online
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
