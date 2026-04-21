from db import get_connection
from argon2 import PasswordHasher 
from argon2.exceptions import VerifyMismatchError

def create_user(username, password):
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


def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    ph = PasswordHasher()

    cursor.execute(
        "SELECT id, password FROM users WHERE username=%s",
        (username,)
    )

    user = cursor.fetchone()
    if user:
        try:
            ph.verify(user[1], password)

            if ph.check_needs_rehash(user[1]):
                new_hash = ph.hash(password)
                cursor.execute(
                    "UPDATE users SET password=%s WHERE id=%s",
                    (new_hash, user[0])
                )
                conn.commit()

            conn.close()
            return user[0]
        except VerifyMismatchError:
            pass

    conn.close()
    return None


def get_balance(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT balance FROM accounts WHERE user_id=%s",
        (user_id,)
    )

    balance = cursor.fetchone()[0]
    conn.close()
    return balance


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