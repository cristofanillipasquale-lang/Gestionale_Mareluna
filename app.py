from flask import Flask, render_template, request, redirect
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

DATABASE = "database.db"

# ------------------------
# DATABASE
# ------------------------
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect(DATABASE)

    conn.execute('''
        CREATE TABLE IF NOT EXISTS camere (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            prezzo REAL
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS prenotazioni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            camera_id INTEGER,
            checkin TEXT,
            checkout TEXT
        )
    ''')

    # Camere base (non si duplicano)
    conn.execute("INSERT OR IGNORE INTO camere (id, nome, prezzo) VALUES (1, 'Camera 1', 50)")
    conn.execute("INSERT OR IGNORE INTO camere (id, nome, prezzo) VALUES (2, 'Camera 2', 70)")

    conn.commit()
    conn.close()

init_db()

# ------------------------
# HOME
# ------------------------
@app.route('/')
def index():
    db = get_db()

    prenotazioni = db.execute('''
        SELECT p.*, c.nome as camera_nome, c.prezzo
        FROM prenotazioni p
        JOIN camere c ON p.camera_id = c.id
        ORDER BY p.checkin DESC
    ''').fetchall()

    camere = db.execute("SELECT * FROM camere").fetchall()

    totale = 0

    for p in prenotazioni:
        d1 = datetime.strptime(p["checkin"], "%Y-%m-%d")
        d2 = datetime.strptime(p["checkout"], "%Y-%m-%d")
        giorni = (d2 - d1).days
        totale += giorni * p["prezzo"]

    return render_template(
        "index.html",
        prenotazioni=prenotazioni,
        camere=camere,
        totale=totale
    )

# ------------------------
# AGGIUNGI
# ------------------------
@app.route('/aggiungi', methods=['POST'])
def aggiungi():
    nome = request.form.get('nome')
    camera_id = request.form.get('camera')
    checkin = request.form.get('checkin')
    checkout = request.form.get('checkout')

    db = get_db()
    db.execute(
        "INSERT INTO prenotazioni (nome, camera_id, checkin, checkout) VALUES (?, ?, ?, ?)",
        (nome, camera_id, checkin, checkout)
    )
    db.commit()

    return redirect('/')

# ------------------------
# ELIMINA
# ------------------------
@app.route('/elimina/<int:id>')
def elimina(id):
    db = get_db()
    db.execute("DELETE FROM prenotazioni WHERE id = ?", (id,))
    db.commit()
    return redirect('/')

# ------------------------
# AVVIO ONLINE
# ------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
