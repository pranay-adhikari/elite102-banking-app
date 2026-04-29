from db import get_connection
from user import User
from flask_login import LoginManager
from argon2 import PasswordHasher 
from argon2.exceptions import VerifyMismatchError
from utils import normalize_username

def create_user(username, password):
    username = normalize_username(username)
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM users WHERE username=%s",
        (username,)
    )
    if cursor.fetchone():
        conn.close()
        return False

    ph = PasswordHasher()
    hash = ph.hash(password)

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s)",
        (username, hash)
    )

    user_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO accounts (user_id, balance) VALUES (%s, %s)",
        (user_id, 0)
    )
    
    conn.commit()
    conn.close()
    return True


def authenticate_user(username, password):
    username = normalize_username(username)
    conn = get_connection()
    cursor = conn.cursor()

    ph = PasswordHasher()

    cursor.execute(
        "SELECT id, username, password FROM users WHERE username=%s",
        (username,)
    )

    row = cursor.fetchone()
    if row:
        try:
            ph.verify(row[2], password)

            if ph.check_needs_rehash(row[2]):
                new_hash = ph.hash(password)
                cursor.execute(
                    "UPDATE users SET password=%s WHERE id=%s",
                    (new_hash, row[0])
                )
                conn.commit()

            conn.close()
            return User(row[0], row[1])
        except VerifyMismatchError:
            pass

    conn.close()
    return None

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, username FROM users WHERE id=%s",
        (user_id,)
    )
    row = cursor.fetchone()

    conn.close()

    if row:
        return User(row[0], row[1])
    return None

def get_balance(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT balance FROM accounts WHERE user_id=%s",
        (user_id,)
    )

    cents = cursor.fetchone()[0]
    conn.close()
    return cents


def deposit(user_id, amount):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE accounts SET balance = balance + %s WHERE user_id=%s",
        (amount, user_id)
    )

    conn.commit()
    conn.close()


def withdraw(user_id, amount):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE accounts SET balance = balance - %s WHERE user_id=%s AND balance >= %s",
        (amount, user_id, amount)
    )

    success = cursor.rowcount > 0

    conn.commit()
    conn.close()
    return success