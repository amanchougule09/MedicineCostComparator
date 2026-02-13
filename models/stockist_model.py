from models.database import Database
from typing import List, Dict


class StockistModel:
    def __init__(self):
        self.db = Database()
    
    def get_all_stockists(self) -> List[Dict]:
        """Get all stockists"""
        return self.db.fetch_all("""
            SELECT id, name, contact, address, gst_no 
            FROM stockists 
            ORDER BY name ASC
        """)
    
    def add_stockist(self, stockist_data: Dict) -> int:
        """Add new stockist"""
        return self.db.insert("""
            INSERT INTO stockists (name, contact, address, gst_no)
            VALUES (?, ?, ?, ?)
        """, (
            stockist_data['name'],
            stockist_data.get('contact', ''),
            stockist_data.get('address', ''),
            stockist_data.get('gst_no', '')
        ))
    
    def get_stockist_medicines(self, stockist_id: int) -> List[Dict]:
        """Get all medicines from a specific stockist"""
        return self.db.fetch_all("""
            SELECT 
                m.medicine_name,
                m.company_name,
                mp.net_rate,
                mp.mrp,
                mp.discount_percent,
                mp.final_price,
                mp.purchase_date
            FROM medicine_prices mp
            JOIN medicines m ON mp.medicine_id = m.id
            WHERE mp.stockist_id = ?
            ORDER BY mp.purchase_date DESC
        """, (stockist_id,))