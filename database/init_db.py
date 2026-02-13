import sqlite3
import os
from datetime import datetime, timedelta
import random


def init_database():
    """Initialize database with all tables and sample data"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'medicine_prices.db')
    
    # Remove existing database if you want fresh start
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ========== CREATE TABLES ==========
    
    # Stockists table
    cursor.execute('''
        CREATE TABLE stockists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT,
            address TEXT,
            gst_no TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Medicines table
    cursor.execute('''
        CREATE TABLE medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_name TEXT NOT NULL,
            company_name TEXT NOT NULL,
            generic_name TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Medicine Prices table
    cursor.execute('''
        CREATE TABLE medicine_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_id INTEGER NOT NULL,
            stockist_id INTEGER NOT NULL,
            net_rate REAL NOT NULL,
            mrp REAL NOT NULL,
            discount_percent REAL DEFAULT 0,
            final_price REAL NOT NULL,
            paid_status TEXT DEFAULT 'Unpaid',
            paid_amount REAL DEFAULT 0,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (medicine_id) REFERENCES medicines (id) ON DELETE CASCADE,
            FOREIGN KEY (stockist_id) REFERENCES stockists (id) ON DELETE CASCADE
        )
    ''')
    
    # Purchases/Savings tracking table
    cursor.execute('''
        CREATE TABLE purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_name TEXT NOT NULL,
            selected_stockist TEXT NOT NULL,
            selected_price REAL NOT NULL,
            lowest_price REAL NOT NULL,
            savings REAL NOT NULL,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ========== INSERT SAMPLE DATA ==========
    
    # Insert stockists
    stockists = [
        ('MediCorp Distributors', '9876543210', 'Mumbai, Maharashtra', '27AABCU9603R1ZM'),
        ('PharmaCare Solutions', '9876543211', 'Delhi, NCR', '07AAFCP4567R1ZL'),
        ('HealthFirst Agencies', '9876543212', 'Bangalore, Karnataka', '29AAAFH1234R1ZB'),
        ('LifeLine Medical', '9876543213', 'Chennai, Tamil Nadu', '33AABCL7890R1ZT'),
        ('Wellness Distributors', '9876543214', 'Kolkata, West Bengal', '19AABCW4567R1ZK'),
        ('MediMart India', '9876543215', 'Pune, Maharashtra', '27AABCM8901R1ZM'),
        ('City Healthcare', '9876543216', 'Hyderabad, Telangana', '36AACCH2345R1ZT'),
        ('Prime Pharma', '9876543217', 'Ahmedabad, Gujarat', '24AAPPP5678R1ZJ'),
        ('Reliable Medicos', '9876543218', 'Jaipur, Rajasthan', '08AARRM9012R1ZR'),
        ('Surgicals & Medicals', '9876543219', 'Lucknow, UP', '09AASSM3456R1ZU')
    ]
    
    cursor.executemany(
        'INSERT INTO stockists (name, contact, address, gst_no) VALUES (?, ?, ?, ?)',
        stockists
    )
    
    # Get stockist IDs
    cursor.execute('SELECT id FROM stockists')
    stockist_ids = [row[0] for row in cursor.fetchall()]
    
    # Insert medicines with multiple prices
    medicines_data = [
        # (medicine_name, company_name, generic_name, category)
        ('Paracetamol 500mg', 'Cipla', 'Paracetamol', 'Analgesic'),
        ('Amoxicillin 250mg', 'GSK', 'Amoxicillin', 'Antibiotic'),
        ('Omeprazole 20mg', 'Sun Pharma', 'Omeprazole', 'Antacid'),
        ('Metformin 500mg', 'Lupin', 'Metformin', 'Antidiabetic'),
        ('Amlodipine 5mg', 'Dr Reddys', 'Amlodipine', 'Antihypertensive'),
        ('Azithromycin 500mg', 'Pfizer', 'Azithromycin', 'Antibiotic'),
        ('Cetirizine 10mg', 'Johnson & Johnson', 'Cetirizine', 'Antihistamine'),
        ('Dolo 650mg', 'Micro Labs', 'Paracetamol', 'Analgesic'),
        ('Vitamin D3 60K', 'Abbott', 'Cholecalciferol', 'Vitamin'),
        ('Calcium Tablet', 'GlaxoSmithKline', 'Calcium Carbonate', 'Supplement'),
        ('B-Complex', 'Merck', 'Vitamin B Complex', 'Vitamin'),
        ('Aspirin 75mg', 'Bayer', 'Aspirin', 'Blood Thinner'),
        ('Atorvastatin 10mg', 'Zydus Cadila', 'Atorvastatin', 'Cholesterol'),
        ('Levothyroxine 50mcg', 'Abbott', 'Levothyroxine', 'Thyroid'),
        ('Pantoprazole 40mg', 'Alkem', 'Pantoprazole', 'Antacid'),
        ('Losartan 50mg', 'Torrent', 'Losartan', 'Antihypertensive'),
        ('Gabapentin 300mg', 'Sun Pharma', 'Gabapentin', 'Neuropathic Pain'),
        ('Diclofenac Gel', 'Volta', 'Diclofenac', 'Anti-inflammatory'),
        ('Cough Syrup', 'Himalaya', 'Herbal', 'Respiratory'),
        ('Insulin Regular', 'Novo Nordisk', 'Insulin', 'Antidiabetic')
    ]
    
    for med in medicines_data:
        cursor.execute('''
            INSERT INTO medicines (medicine_name, company_name, generic_name, category)
            VALUES (?, ?, ?, ?)
        ''', med)
        medicine_id = cursor.lastrowid
        
        # Each medicine will have prices from 3-5 random stockists
        num_stockists = random.randint(3, 6)
        selected_stockists = random.sample(stockist_ids, min(num_stockists, len(stockist_ids)))
        
        for stockist_id in selected_stockists:
            # Generate realistic prices
            base_price = random.uniform(10, 500)
            mrp = round(base_price * random.uniform(1.15, 1.35), 2)
            discount = random.choice([0, 2.5, 5, 7.5, 10, 12.5, 15])
            final_price = round(mrp * (1 - discount/100), 2)
            net_rate = round(final_price * 0.9, 2)  # Approximate net rate
            
            # Random purchase date within last 30 days
            days_ago = random.randint(0, 30)
            purchase_date = datetime.now() - timedelta(days=days_ago)
            
            cursor.execute('''
                INSERT INTO medicine_prices 
                (medicine_id, stockist_id, net_rate, mrp, discount_percent, 
                 final_price, paid_status, paid_amount, purchase_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                medicine_id,
                stockist_id,
                net_rate,
                mrp,
                discount,
                final_price,
                random.choice(['Paid', 'Unpaid', 'Half Paid']),
                round(final_price * random.uniform(0.5, 1), 2) if random.random() > 0.5 else 0,
                purchase_date.strftime('%Y-%m-%d %H:%M:%S')
            ))
    
    # Insert sample purchases
    cursor.execute('SELECT medicine_name FROM medicines')
    medicines = cursor.fetchall()
    
    for _ in range(50):  # 50 sample purchases
        medicine = random.choice(medicines)
        medicine_name = medicine[0]
        
        # Get all prices for this medicine
        cursor.execute('''
            SELECT s.name, mp.final_price 
            FROM medicine_prices mp
            JOIN stockists s ON mp.stockist_id = s.id
            JOIN medicines m ON mp.medicine_id = m.id
            WHERE m.medicine_name = ?
        ''', (medicine_name,))
        
        prices = cursor.fetchall()
        
        if len(prices) >= 2:
            # Find lowest price
            lowest_price = min(p[1] for p in prices)
            # Select random price (maybe not the lowest)
            selected = random.choice(prices)
            savings = lowest_price - selected[1]
            
            days_ago = random.randint(1, 30)
            purchase_date = datetime.now() - timedelta(days=days_ago)
            
            cursor.execute('''
                INSERT INTO purchases 
                (medicine_name, selected_stockist, selected_price, lowest_price, savings, purchase_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                medicine_name,
                selected[0],
                selected[1],
                lowest_price,
                savings,
                purchase_date.strftime('%Y-%m-%d %H:%M:%S')
            ))
    
    conn.commit()
    conn.close()
    
    print("=" * 50)
    print("✅ Database initialized successfully!")
    print(f"📁 Location: {db_path}")
    print(f"📊 Tables created: stockists, medicines, medicine_prices, purchases")
    print(f"🏢 Stockists added: {len(stockists)}")
    print(f"💊 Medicines added: {len(medicines_data)}")
    print("=" * 50)


if __name__ == '__main__':
    init_database()