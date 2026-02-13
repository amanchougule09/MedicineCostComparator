from models.database import Database
from typing import List, Dict, Any


class MedicineModel:
    def __init__(self):
        self.db = Database()
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get statistics for dashboard"""
        
        # Total unique medicines
        total_medicines = self.db.fetch_one("""
            SELECT COUNT(DISTINCT medicine_name) as count 
            FROM medicines
        """)['count']
        
        # Total stockists
        total_stockists = self.db.fetch_one("""
            SELECT COUNT(*) as count 
            FROM stockists
        """)['count']
        
        # Total purchases and savings
        purchase_stats = self.db.fetch_one("""
            SELECT 
                COUNT(*) as total_purchases,
                COALESCE(SUM(savings), 0) as total_savings,
                COALESCE(AVG(savings), 0) as avg_savings
            FROM purchases
        """)
        
        # Today's best deals (lowest prices)
        best_deals = self.db.fetch_all("""
            SELECT 
                m.medicine_name,
                m.company_name,
                s.name as stockist_name,
                MIN(mp.final_price) as price,
                mp.mrp,
                (mp.mrp - mp.final_price) as savings,
                mp.discount_percent
            FROM medicine_prices mp
            JOIN medicines m ON mp.medicine_id = m.id
            JOIN stockists s ON mp.stockist_id = s.id
            WHERE date(mp.purchase_date) = date('now')
            GROUP BY m.id
            ORDER BY mp.final_price ASC
            LIMIT 5
        """)
        
        # Recently added medicines
        recent_medicines = self.db.fetch_all("""
            SELECT 
                medicine_name,
                company_name,
                created_at
            FROM medicines
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        return {
            'total_medicines': total_medicines,
            'total_stockists': total_stockists,
            'total_purchases': purchase_stats['total_purchases'],
            'total_savings': round(purchase_stats['total_savings'], 2),
            'avg_savings': round(purchase_stats['avg_savings'], 2),
            'best_deals': best_deals,
            'recent_medicines': recent_medicines
        }
    
    def search_lowest_price(self, search_term: str) -> List[Dict]:
        """Search medicine and get lowest price from all stockists"""
        
        return self.db.fetch_all("""
            WITH PriceRanks AS (
                SELECT 
                    m.id,
                    m.medicine_name,
                    m.company_name,
                    m.generic_name,
                    s.name as stockist_name,
                    s.id as stockist_id,
                    mp.final_price,
                    mp.mrp,
                    mp.discount_percent,
                    (mp.mrp - mp.final_price) as savings,
                    ROW_NUMBER() OVER (PARTITION BY m.id ORDER BY mp.final_price ASC) as price_rank
                FROM medicines m
                JOIN medicine_prices mp ON m.id = mp.medicine_id
                JOIN stockists s ON mp.stockist_id = s.id
                WHERE m.medicine_name LIKE ? OR m.generic_name LIKE ? OR m.company_name LIKE ?
            )
            SELECT *
            FROM PriceRanks
            WHERE price_rank = 1
            ORDER BY medicine_name ASC
        """, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
    
    def get_all_stockist_prices(self, medicine_id: int) -> List[Dict]:
        """Get all prices for a medicine from different stockists"""
        
        return self.db.fetch_all("""
            SELECT 
                s.name as stockist_name,
                s.contact,
                s.address,
                mp.net_rate,
                mp.mrp,
                mp.discount_percent,
                mp.final_price,
                mp.purchase_date,
                RANK() OVER (ORDER BY mp.final_price ASC) as price_rank
            FROM medicine_prices mp
            JOIN stockists s ON mp.stockist_id = s.id
            WHERE mp.medicine_id = ?
            ORDER BY mp.final_price ASC
        """, (medicine_id,))
    
    def add_medicine(self, medicine_data: Dict) -> int:
        """Add new medicine"""
        
        medicine_id = self.db.insert("""
            INSERT INTO medicines 
            (medicine_name, company_name, generic_name, category)
            VALUES (?, ?, ?, ?)
        """, (
            medicine_data['medicine_name'],
            medicine_data['company_name'],
            medicine_data.get('generic_name', ''),
            medicine_data.get('category', '')
        ))
        
        return medicine_id
    
    def add_medicine_price(self, medicine_id: int, price_data: Dict):
        """Add price for medicine from stockist"""
        
        final_price = price_data['mrp'] * (1 - price_data.get('discount_percent', 0) / 100)
        
        self.db.insert("""
            INSERT INTO medicine_prices 
            (medicine_id, stockist_id, net_rate, mrp, discount_percent, 
             final_price, paid_status, paid_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            medicine_id,
            price_data['stockist_id'],
            price_data['net_rate'],
            price_data['mrp'],
            price_data.get('discount_percent', 0),
            final_price,
            price_data.get('paid_status', 'Unpaid'),
            price_data.get('paid_amount', 0)
        ))
    
    def get_all_medicines_with_prices(self) -> List[Dict]:
        """Get all medicines with their lowest prices"""
        
        return self.db.fetch_all("""
            SELECT DISTINCT
                m.id,
                m.medicine_name,
                m.company_name,
                m.generic_name,
                MIN(mp.final_price) as lowest_price,
                COUNT(DISTINCT mp.stockist_id) as stockist_count,
                MIN(mp.mrp) as mrp
            FROM medicines m
            LEFT JOIN medicine_prices mp ON m.id = mp.medicine_id
            GROUP BY m.id
            ORDER BY m.medicine_name ASC
        """)
    
    def record_purchase(self, medicine_name: str, stockist_name: str, 
                       paid_price: float, lowest_price: float):
        """Record purchase and calculate savings"""
        
        savings = lowest_price - paid_price  # Positive if saved money
        
        self.db.insert("""
            INSERT INTO purchases 
            (medicine_name, selected_stockist, selected_price, lowest_price, savings)
            VALUES (?, ?, ?, ?, ?)
        """, (medicine_name, stockist_name, paid_price, lowest_price, savings))
        
        return savings