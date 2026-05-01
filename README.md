# E102 Banking App

A simple banking web app built with Flask and MySQL for Elite 102.

## Features
- User registration and login with secure password hashing (Argon2)
- Deposit and withdrawal with balance validation
- Transaction history

## Prerequisites
- Python 3.x
- MySQL
- Redis (for session storage)

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/pranay-adhikari/elite102-banking-app.git
cd elite102-banking-app
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
Copy the `.env.example` file to `.env` in the root directory and fill in your values

### 4. Set up the database
Create a MySQL database, then run the following SQL to create the tables:

```sql
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `accounts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `balance` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `accounts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `transactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `type` enum('deposit','withdraw') NOT NULL,
  `amount` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 5. Start Redis

```bash
redis-server
```

### 6. Run the app

```bash
python src/app.py
```

The app will be available at http://localhost:5000