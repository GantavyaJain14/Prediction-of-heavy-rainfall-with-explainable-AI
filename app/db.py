"""
db.py – SQLite database helper for user authentication.

Creates the `users` table on first run and provides
sign-up and sign-in helper functions.
"""
import sqlite3
import hashlib
import os

# Database file lives alongside app.py inside the `app/` directory
DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')


def get_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # allows dict-like access to rows
    return conn


def init_db():
    """Create the users table if it does not already exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            email       TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,       -- SHA-256 hex digest
            created_at  DATETIME DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()
    print("✅ [DB] users table ready.")


def hash_password(password: str) -> str:
    """Return the SHA-256 hash of the given plain-text password."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def register_user(name: str, email: str, password: str) -> dict:
    """
    Insert a new user into the database.

    Returns:
        {'success': True}                         – on success
        {'success': False, 'error': '<message>'}  – on failure (e.g. duplicate email)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name.strip(), email.strip().lower(), hash_password(password))
        )
        conn.commit()
        conn.close()
        return {'success': True}
    except sqlite3.IntegrityError:
        return {'success': False, 'error': 'An account with this email already exists.'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def verify_user(email: str, password: str) -> dict:
    """
    Check credentials against the database.

    Returns:
        {'success': True,  'user': {'id', 'name', 'email'}}  – on valid credentials
        {'success': False, 'error': '<message>'}              – on failure
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, email, password FROM users WHERE email = ?",
        (email.strip().lower(),)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return {'success': False, 'error': 'No account found with this email.'}

    if row['password'] != hash_password(password):
        return {'success': False, 'error': 'Incorrect password.'}

    return {
        'success': True,
        'user': {'id': row['id'], 'name': row['name'], 'email': row['email']}
    }
