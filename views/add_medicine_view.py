from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, 
    QComboBox, QSpinBox, QDoubleSpinBox, QMessageBox, QGroupBox, QFormLayout
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont


class AddMedicineView(QWidget):
    medicine_added = pyqtSignal()
    back_to_dashboard = pyqtSignal()
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.stockists = []
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
        title = QLabel("Add New Medicine")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Form group
        form_group = QGroupBox("Medicine Details")
        form_layout = QFormLayout()
        
        # Medicine Name
        self.medicine_name_input = QLineEdit()
        self.medicine_name_input.setPlaceholderText("e.g., Aspirin")
        form_layout.addRow("Medicine Name:", self.medicine_name_input)
        
        # Company Name
        self.company_name_input = QLineEdit()
        self.company_name_input.setPlaceholderText("e.g., Bayer")
        form_layout.addRow("Company Name:", self.company_name_input)
        
        # Stockist Selection
        self.stockist_combo = QComboBox()
        self.stockist_combo.setMinimumWidth(300)
        form_layout.addRow("Stockist:", self.stockist_combo)
        
        # Net Rate
        self.net_rate_input = QDoubleSpinBox()
        self.net_rate_input.setMaximum(99999.99)
        self.net_rate_input.setSuffix(" ₹")
        form_layout.addRow("Net Rate:", self.net_rate_input)
        
        # MRP
        self.mrp_input = QDoubleSpinBox()
        self.mrp_input.setMaximum(99999.99)
        self.mrp_input.setSuffix(" ₹")
        form_layout.addRow("MRP:", self.mrp_input)
        
        # Discount
        self.discount_input = QSpinBox()
        self.discount_input.setMaximum(100)
        self.discount_input.setSuffix(" %")
        form_layout.addRow("Discount %:", self.discount_input)
        
        # Quantity
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(10000)
        form_layout.addRow("Quantity:", self.quantity_input)
        
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Medicine")
        add_btn.setMinimumWidth(150)
        add_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        add_btn.clicked.connect(self.on_add_medicine)
        
        clear_btn = QPushButton("Clear")
        clear_btn.setMinimumWidth(150)
        clear_btn.clicked.connect(self.clear_form)
        
        button_layout.addStretch()
        button_layout.addWidget(add_btn)
        button_layout.addWidget(clear_btn)
        
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def load_stockists(self):
        """Load stockists into combo box"""
        try:
            self.stockists = self.controller.get_all_stockists()
            self.stockist_combo.clear()
            
            if self.stockists:
                for stockist in self.stockists:
                    self.stockist_combo.addItem(stockist['name'], stockist['id'])
            else:
                self.stockist_combo.addItem("No stockists available")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load stockists: {str(e)}")
    
    def on_add_medicine(self):
        """Add new medicine"""
        if not self.medicine_name_input.text().strip():
            QMessageBox.warning(self, "Validation", "Please enter medicine name")
            return
        
        if not self.company_name_input.text().strip():
            QMessageBox.warning(self, "Validation", "Please enter company name")
            return
        
        if not self.stockists:
            QMessageBox.warning(self, "Validation", "No stockists available")
            return
        
        try:
            medicine_data = {
                'medicine_name': self.medicine_name_input.text().strip(),
                'company_name': self.company_name_input.text().strip()
            }
            
            price_data = {
                'stockist_id': self.stockist_combo.currentData(),
                'net_rate': self.net_rate_input.value(),
                'mrp': self.mrp_input.value(),
                'discount_percent': self.discount_input.value(),
                'quantity': self.quantity_input.value()
            }
            
            self.controller.add_new_medicine(medicine_data, price_data)
            QMessageBox.information(self, "Success", "Medicine added successfully!")
            self.clear_form()
            self.medicine_added.emit()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add medicine: {str(e)}")
    
    def clear_form(self):
        """Clear all form fields"""
        self.medicine_name_input.clear()
        self.company_name_input.clear()
        self.net_rate_input.setValue(0)
        self.mrp_input.setValue(0)
        self.discount_input.setValue(0)
        self.quantity_input.setValue(1)
    
    def on_back_clicked(self):
        """Emit back_to_dashboard signal"""
        self.back_to_dashboard.emit()
