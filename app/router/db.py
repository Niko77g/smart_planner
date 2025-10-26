import sqlite3
import uuid

def init_db():
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        date TEXT NOT NULL,
        start INTEGER NOT NULL,
        end INTEGER NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def add_event(title, date, start, end):
    event_id = str(uuid.uuid4())
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO events (id, title, date, start, end) VALUES (?,?,?,?,?)",
        (event_id, title, date, start, end)
    )
    conn.commit()
    conn.close()
    return event_id

def remove_event(event_id):
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()