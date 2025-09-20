import sqlite3
from datetime import datetime, timedelta
import random

# Connect to SQLite (file in project root)
conn = sqlite3.connect('crowdfunding.db')
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Projects (
    id TEXT PRIMARY KEY,  -- 8 digits, first not 0
    name TEXT NOT NULL,
    goal INTEGER NOT NULL CHECK (goal > 0),
    deadline DATE NOT NULL,
    current_funded INTEGER DEFAULT 0,
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES Categories(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS RewardTiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    min_amount INTEGER NOT NULL,
    quota_remaining INTEGER NOT NULL,
    project_id TEXT,
    FOREIGN KEY (project_id) REFERENCES Projects(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Pledges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    project_id TEXT,
    timestamp DATETIME NOT NULL,
    amount INTEGER NOT NULL,
    reward_tier_id INTEGER,
    status TEXT NOT NULL CHECK (status IN ('success', 'rejected')),
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (project_id) REFERENCES Projects(id),
    FOREIGN KEY (reward_tier_id) REFERENCES RewardTiers(id)
)
""")

# Insert sample data

# Categories (>=3)
categories = ['Technology', 'Education', 'Art', 'Health']
for cat in categories:
    cursor.execute("INSERT OR IGNORE INTO Categories (name) VALUES (?)", (cat,))
conn.commit()

# Fetch category ids
cursor.execute("SELECT id, name FROM Categories")
cat_rows = cursor.fetchall()
cat_ids = {name: id for id, name in cat_rows}

# Users (>=10, simple passwords)
users = [('user1', 'pass1'), ('user2', 'pass2'), ('user3', 'pass3'), ('user4', 'pass4'), ('user5', 'pass5'),
         ('user6', 'pass6'), ('user7', 'pass7'), ('user8', 'pass8'), ('user9', 'pass9'), ('user10', 'pass10')]
for u, p in users:
    cursor.execute("INSERT OR IGNORE INTO Users (username, password) VALUES (?, ?)", (u, p))
conn.commit()

# Fetch user ids
cursor.execute("SELECT id, username FROM Users")
user_rows = cursor.fetchall()
user_ids = {u: id for id, u in user_rows}

# Projects (>=8, cover >=3 categories)
projects = [
    ('12345678', 'Tech Gadget', 100000, datetime.now() + timedelta(days=30), random.choice(list(cat_ids.values()))),
    ('23456789', 'Edu App', 50000, datetime.now() + timedelta(days=15), random.choice(list(cat_ids.values()))),
    ('34567890', 'Art Exhibition', 200000, datetime.now() + timedelta(days=45), random.choice(list(cat_ids.values()))),
    ('45678901', 'Health Device', 150000, datetime.now() + timedelta(days=20), random.choice(list(cat_ids.values()))),
    ('56789012', 'Coding Camp', 80000, datetime.now() + timedelta(days=10), random.choice(list(cat_ids.values()))),
    ('67890123', 'Music Festival', 300000, datetime.now() + timedelta(days=60), random.choice(list(cat_ids.values()))),
    ('78901234', 'Fitness App', 120000, datetime.now() + timedelta(days=25), random.choice(list(cat_ids.values()))),
    ('89012345', 'Book Publishing', 90000, datetime.now() + timedelta(days=35), random.choice(list(cat_ids.values()))),
    ('90123456', 'Eco Project', 250000, datetime.now() + timedelta(days=50), random.choice(list(cat_ids.values())))
]
for pid, name, goal, deadline, cat_id in projects:
    cursor.execute("INSERT OR IGNORE INTO Projects (id, name, goal, deadline, category_id) VALUES (?, ?, ?, ?, ?)",
                   (pid, name, goal, deadline.date(), cat_id))
conn.commit()

# RewardTiers (2-3 per project)
for pid in [p[0] for p in projects]:
    tiers = [
        ('Basic', 100, 50),
        ('Standard', 500, 30),
        ('Premium', 1000, 10)
    ]
    for name, min_amt, quota in tiers:
        cursor.execute("INSERT INTO RewardTiers (name, min_amount, quota_remaining, project_id) VALUES (?, ?, ?, ?)",
                       (name, min_amt, quota, pid))
conn.commit()

# Pledges (mixed success/rejected, for random users/projects)
for _ in range(50):  # Many pledges
    user_id = random.choice(list(user_ids.values()))
    project_id = random.choice([p[0] for p in projects])
    amount = random.randint(50, 2000)
    cursor.execute("SELECT id FROM RewardTiers WHERE project_id=?", (project_id,))
    tier_ids = [t[0] for t in cursor.fetchall()]
    reward_id = random.choice(tier_ids) if tier_ids else None
    timestamp = datetime.now() - timedelta(days=random.randint(1, 30))
    
    # Simulate business rules for sample data
    cursor.execute("SELECT deadline FROM Projects WHERE id=?", (project_id,))
    deadline = cursor.fetchone()[0]
    deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
    if deadline_date < datetime.now().date():
        status = 'rejected'
    else:
        if reward_id:
            cursor.execute("SELECT min_amount FROM RewardTiers WHERE id=?", (reward_id,))
            min_amt = cursor.fetchone()[0]
            if amount < min_amt:
                status = 'rejected'
            else:
                status = 'success'
        else:
            status = 'success'
    
    cursor.execute("INSERT INTO Pledges (user_id, project_id, timestamp, amount, reward_tier_id, status) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, project_id, timestamp, amount, reward_id, status))
conn.commit()

# Update current_funded based on success pledges
for pid in [p[0] for p in projects]:
    cursor.execute("SELECT SUM(amount) FROM Pledges WHERE project_id=? AND status='success'", (pid,))
    total = cursor.fetchone()[0] or 0
    cursor.execute("UPDATE Projects SET current_funded=? WHERE id=?", (total, pid))
conn.commit()

conn.close()
print("Database initialized with sample data.")