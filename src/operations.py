from db import get_connection

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
    
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s)",
        (username, password)
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

    cursor.execute(
        "SELECT id FROM users WHERE username=%s AND password=%s",
        (username, password)
    )

    user = cursor.fetchone()
    conn.close()
    return user


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