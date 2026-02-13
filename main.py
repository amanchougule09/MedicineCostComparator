import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt5.QtCore import Qt

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controllers.dashboard_controller import DashboardController
from views.dashboard_view import DashboardView
from views.add_medicine_view import AddMedicineView
from views.medicine_list_view import MedicineListView
from database.init_db import init_database


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medicine Price Comparator - Doctor's Dashboard")
        self.setMinimumSize(1200, 800)
        
        # Initialize database
        try:
            init_database()
        except Exception as e:
            QMessageBox.warning(None, "Database", f"Database initialized: {str(e)}")
        
        # Setup stacked widget for views
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Initialize controllers
        self.dashboard_controller = DashboardController(self)
        
        # Initialize views
        self.dashboard_view = DashboardView(self.dashboard_controller)
        self.add_medicine_view = AddMedicineView(self.dashboard_controller)
        self.medicine_list_view = MedicineListView(self.dashboard_controller)
        
        # Add views to stacked widget
        self.stacked_widget.addWidget(self.dashboard_view)
        self.stacked_widget.addWidget(self.add_medicine_view)
        self.stacked_widget.addWidget(self.medicine_list_view)
        
        # Connect signals
        self.connect_signals()
        
        # Show dashboard first
        self.show_dashboard()
        
        # Apply global styles
        self.apply_styles()
    
    def connect_signals(self):
        """Connect view signals to controller methods"""
        # Dashboard signals
        self.dashboard_view.switch_to_add_medicine.connect(self.show_add_medicine)
        self.dashboard_view.switch_to_all_medicines.connect(self.show_all_medicines)
        self.dashboard_view.medicine_selected.connect(self.on_medicine_selected)
        
        # Add medicine signals
        self.add_medicine_view.medicine_added.connect(self.on_medicine_added)
        self.add_medicine_view.back_to_dashboard.connect(self.show_dashboard)
        
        # Medicine list signals
        self.medicine_list_view.back_to_dashboard.connect(self.show_dashboard)
    
    def show_dashboard(self):
        self.stacked_widget.setCurrentWidget(self.dashboard_view)
        self.dashboard_view.refresh_data()
    
    def show_add_medicine(self):
        self.stacked_widget.setCurrentWidget(self.add_medicine_view)
        self.add_medicine_view.load_stockists()
    
    def show_all_medicines(self):
        self.stacked_widget.setCurrentWidget(self.medicine_list_view)
        self.medicine_list_view.load_medicines()
    
    def on_medicine_selected(self, medicine_data):
        """Handle medicine selection from dashboard search"""
        self.show_all_medicines()
        self.medicine_list_view.highlight_medicine(medicine_data)
    
    def on_medicine_added(self):
        """Refresh dashboard when new medicine added"""
        QMessageBox.information(self, "Success", "Medicine added successfully!")
        self.show_dashboard()
    
    def apply_styles(self):
        """Apply global stylesheet"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            
            QStackedWidget {
                background-color: transparent;
            }
            
            /* Custom scrollbar */
            QScrollBar:vertical {
                border: none;
                background: #e9ecef;
                width: 10px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:vertical {
                background: #adb5bd;
                border-radius: 5px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #6c757d;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()