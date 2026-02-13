from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QLineEdit
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QColor


class MedicineListView(QWidget):
    back_to_dashboard = pyqtSignal()
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.medicines = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Header with back button
        header_layout = QHBoxLayout()
        
        # Back button
        back_btn = QPushButton("← Back to Dashboard")
        back_btn.setMaximumWidth(200)
        back_btn.clicked.connect(self.on_back_clicked)
        header_layout.addWidget(back_btn)
        
        # Title
        title = QLabel("All Medicines")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search medicines...")
        self.search_input.setMaximumWidth(300)
        self.search_input.textChanged.connect(self.on_search)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        main_layout.addLayout(search_layout)
        
        # Table widget
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Medicine Name",
            "Company",
            "Generic Name",
            "Lowest Price",
            "MRP",
            "Available At (Stockists)"
        ])
        
        # Configure table
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #ddd;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #4e73df;
                color: white;
                padding: 5px;
                border: none;
            }
        """)
        
        main_layout.addWidget(self.table)
        
        # Summary
        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("color: #666; font-style: italic;")
        main_layout.addWidget(self.summary_label)
        
        # Refresh button
        refresh_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setMaximumWidth(150)
        refresh_btn.clicked.connect(self.load_medicines)
        refresh_layout.addStretch()
        refresh_layout.addWidget(refresh_btn)
        main_layout.addLayout(refresh_layout)
        
        self.setLayout(main_layout)
    
    def load_medicines(self):
        """Load medicines into table"""
        try:
            # Get all medicines from database
            self.medicines = self.controller.medicine_model.get_all_medicines_with_prices()
            self.display_medicines(self.medicines)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load medicines: {str(e)}")
    
    def display_medicines(self, medicines):
        """Display medicines in table"""
        self.table.setRowCount(0)
        
        if not medicines:
            self.summary_label.setText("No medicines found")
            return
        
        for row, medicine in enumerate(medicines):
            self.table.insertRow(row)
            
            # Medicine Name
            item = QTableWidgetItem(medicine.get('medicine_name', 'N/A'))
            self.table.setItem(row, 0, item)
            
            # Company
            item = QTableWidgetItem(medicine.get('company_name', 'N/A'))
            self.table.setItem(row, 1, item)
            
            # Generic Name
            item = QTableWidgetItem(medicine.get('generic_name', 'N/A'))
            self.table.setItem(row, 2, item)
            
            # Lowest Price
            lowest_price = medicine.get('lowest_price', 0)
            if lowest_price:
                item = QTableWidgetItem(f"₹ {lowest_price:.2f}")
            else:
                item = QTableWidgetItem("N/A")
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, item)
            
            # MRP
            mrp = medicine.get('mrp', 0)
            if mrp:
                item = QTableWidgetItem(f"₹ {mrp:.2f}")
            else:
                item = QTableWidgetItem("N/A")
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, item)
            
            # Stockist Count
            stockist_count = medicine.get('stockist_count', 0)
            item = QTableWidgetItem(f"{stockist_count} stockists")
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, item)
        
        self.summary_label.setText(f"Total medicines: {len(medicines)}")
    
    def on_search(self):
        """Filter medicines based on search"""
        search_text = self.search_input.text().lower().strip()
        
        if not search_text:
            self.display_medicines(self.medicines)
            return
        
        filtered = [
            m for m in self.medicines
            if search_text in m.get('medicine_name', '').lower() or
               search_text in m.get('company_name', '').lower() or
               search_text in m.get('generic_name', '').lower()
        ]
        
        self.display_medicines(filtered)
    
    def highlight_medicine(self, medicine_data):
        """Highlight a specific medicine"""
        if not medicine_data:
            return
        
        medicine_name = medicine_data.get('medicine_name', '')
        
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == medicine_name:
                self.table.selectRow(row)
                self.table.scrollToItem(self.table.item(row, 0))
                break
    
    def on_back_clicked(self):
        """Emit back_to_dashboard signal"""
        self.back_to_dashboard.emit()
