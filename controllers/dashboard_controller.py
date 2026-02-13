from models.medicine_model import MedicineModel
from models.stockist_model import StockistModel


class DashboardController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.medicine_model = MedicineModel()
        self.stockist_model = StockistModel()
    
    def get_dashboard_stats(self):
        """Get all statistics for dashboard"""
        return self.medicine_model.get_dashboard_stats()
    
    def search_medicines(self, search_term):
        """Search medicines with lowest prices"""
        if not search_term or len(search_term.strip()) < 2:
            return []
        return self.medicine_model.search_lowest_price(search_term.strip())
    
    def get_all_stockists(self):
        """Get all stockists for dropdown"""
        return self.stockist_model.get_all_stockists()
    
    def add_new_medicine(self, medicine_data, price_data):
        """Add new medicine with price"""
        # Add medicine
        medicine_id = self.medicine_model.add_medicine(medicine_data)
        
        # Add price
        self.medicine_model.add_medicine_price(medicine_id, price_data)
        
        return medicine_id
    
    def record_purchase(self, medicine_name, stockist_name, paid_price, lowest_price):
        """Record a purchase and calculate savings"""
        return self.medicine_model.record_purchase(
            medicine_name, stockist_name, paid_price, lowest_price
        )