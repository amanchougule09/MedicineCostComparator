from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QLineEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QSpacerItem,
    QSizePolicy, QMessageBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon


class DashboardView(QWidget):
    # Signals
    switch_to_add_medicine = pyqtSignal()
    switch_to_all_medicines = pyqtSignal()
    medicine_selected = pyqtSignal(dict)
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()
        
        # Auto refresh every 30 seconds
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)
    
    def setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        
        # ========== HEADER SECTION ==========
        header_frame = self.create_header()
        main_layout.addWidget(header_frame)
        
        # ========== STATISTICS CARDS ==========
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.total_medicines_card = self.create_stat_card("💊", "Total Medicines", "0", "#4e73df")
        self.total_stockists_card = self.create_stat_card("🏢", "Total Stockists", "0", "#1cc88a")
        self.total_savings_card = self.create_stat_card("💰", "Total Savings", "₹0", "#f6c23e")
        self.avg_savings_card = self.create_stat_card("📊", "Avg Savings", "₹0", "#e74a3b")
        
        stats_layout.addWidget(self.total_medicines_card)
        stats_layout.addWidget(self.total_stockists_card)
        stats_layout.addWidget(self.total_savings_card)
        stats_layout.addWidget(self.avg_savings_card)
        
        main_layout.addLayout(stats_layout)
        
        # ========== SEARCH SECTION ==========
        search_group = self.create_search_section()
        main_layout.addWidget(search_group)
        
        # ========== TWO COLUMN LAYOUT ==========
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(25)
        
        # Left Column - Best Deals
        left_column = self.create_best_deals_section()
        columns_layout.addWidget(left_column, 1)
        
        # Right Column - Recent Medicines & Actions
        right_column = self.create_right_column()
        columns_layout.addWidget(right_column, 1)
        
        main_layout.addLayout(columns_layout, 1)
        
        # ========== QUICK ACTIONS ==========
        actions_layout = self.create_quick_actions()
        main_layout.addLayout(actions_layout)
        
        self.setLayout(main_layout)
        self.apply_styles()
    
    def create_header(self):
        """Create header section"""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        
        # Title section
        title_container = QVBoxLayout()
        
        welcome_label = QLabel("Welcome back, Dr.")
        welcome_label.setObjectName("welcomeLabel")
        
        title = QLabel("Medicine Price Comparator")
        title.setObjectName("mainTitle")
        
        subtitle = QLabel("Find the lowest medicine prices across all stockists")
        subtitle.setObjectName("subTitle")
        
        title_container.addWidget(welcome_label)
        title_container.addWidget(title)
        title_container.addWidget(subtitle)
        
        # Date and time
        date_label = QLabel("Today's Date")
        date_label.setObjectName("dateLabel")
        from datetime import datetime
        date_label.setText(datetime.now().strftime("%A, %B %d, %Y"))
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        header_layout.addWidget(date_label)
        
        return header_frame
    
    def create_stat_card(self, icon, title, value, color):
        """Create a statistics card"""
        card = QFrame()
        card.setObjectName("statCard")
        card.setMinimumHeight(120)
        card.setMaximumHeight(120)
        
        layout = QHBoxLayout(card)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setObjectName("statIcon")
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 32px;
                background-color: {color}20;
                padding: 15px;
                border-radius: 15px;
            }}
        """)
        
        # Text content
        text_layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        
        self.stat_value = QLabel(value)
        self.stat_value.setObjectName("statValue")
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(self.stat_value)
        
        # Store reference to value label
        if title == "Total Medicines":
            self.total_medicines_value = self.stat_value
        elif title == "Total Stockists":
            self.total_stockists_value = self.stat_value
        elif title == "Total Savings":
            self.total_savings_value = self.stat_value
        elif title == "Avg Savings":
            self.avg_savings_value = self.stat_value
        
        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        layout.addStretch()
        
        return card
    
    def create_search_section(self):
        """Create search section"""
        search_group = QGroupBox("🔍 Find Lowest Price Medicine")
        search_group.setObjectName("searchGroup")
        
        layout = QVBoxLayout(search_group)
        
        # Search bar
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter medicine name (e.g., Paracetamol, Amoxicillin...)")
        self.search_input.setMinimumHeight(50)
        self.search_input.returnPressed.connect(self.perform_search)
        
        search_button = QPushButton("🔍 Find Best Price")
        search_button.setMinimumHeight(50)
        search_button.setMinimumWidth(200)
        search_button.setObjectName("searchButton")
        search_button.clicked.connect(self.perform_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setObjectName("resultsTable")
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Medicine Name", "Company", "Stockist", "MRP", "Our Price", "Savings"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setMinimumHeight(200)
        self.results_table.hide()
        
        layout.addLayout(search_layout)
        layout.addWidget(self.results_table)
        
        return search_group
    
    def create_best_deals_section(self):
        """Create best deals section"""
        frame = QFrame()
        frame.setObjectName("bestDealsFrame")
        
        layout = QVBoxLayout(frame)
        
        title = QLabel("🏆 Today's Best Deals")
        title.setObjectName("sectionTitle")
        
        self.best_deals_list = QListWidget()
        self.best_deals_list.setObjectName("bestDealsList")
        self.best_deals_list.setMinimumHeight(300)
        
        layout.addWidget(title)
        layout.addWidget(self.best_deals_list)
        
        return frame
    
    def create_right_column(self):
        """Create right column with recent medicines and actions"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setSpacing(20)
        
        # Recent Medicines
        recent_frame = QFrame()
        recent_frame.setObjectName("recentFrame")
        recent_layout = QVBoxLayout(recent_frame)
        
        recent_title = QLabel("🕒 Recently Added Medicines")
        recent_title.setObjectName("sectionTitle")
        
        self.recent_medicines_list = QListWidget()
        self.recent_medicines_list.setObjectName("recentList")
        self.recent_medicines_list.setMinimumHeight(200)
        
        recent_layout.addWidget(recent_title)
        recent_layout.addWidget(self.recent_medicines_list)
        
        # Quick Stats
        stats_frame = QFrame()
        stats_frame.setObjectName("quickStatsFrame")
        stats_layout = QVBoxLayout(stats_frame)
        
        stats_title = QLabel("📈 Quick Statistics")
        stats_title.setObjectName("sectionTitle")
        
        self.total_purchases_label = QLabel("Total Purchases: 0")
        self.total_saved_label = QLabel("Total Money Saved: ₹0")
        
        stats_layout.addWidget(stats_title)
        stats_layout.addWidget(self.total_purchases_label)
        stats_layout.addWidget(self.total_saved_label)
        stats_layout.addStretch()
        
        layout.addWidget(recent_frame)
        layout.addWidget(stats_frame)
        
        return frame
    
    def create_quick_actions(self):
        """Create quick actions buttons"""
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        
        add_btn = QPushButton("➕ Add New Medicine")
        add_btn.setObjectName("actionButton")
        add_btn.setMinimumHeight(45)
        add_btn.clicked.connect(self.switch_to_add_medicine.emit)
        
        view_btn = QPushButton("📋 View All Medicines")
        view_btn.setObjectName("actionButton")
        view_btn.setMinimumHeight(45)
        view_btn.clicked.connect(self.switch_to_all_medicines.emit)
        
        refresh_btn = QPushButton("🔄 Refresh Data")
        refresh_btn.setObjectName("actionButton")
        refresh_btn.setMinimumHeight(45)
        refresh_btn.clicked.connect(self.refresh_data)
        
        actions_layout.addStretch()
        actions_layout.addWidget(add_btn)
        actions_layout.addWidget(view_btn)
        actions_layout.addWidget(refresh_btn)
        actions_layout.addStretch()
        
        return actions_layout
    
    def refresh_data(self):
        """Refresh dashboard data"""
        stats = self.controller.get_dashboard_stats()
        
        # Update stat cards
        self.total_medicines_value.setText(str(stats['total_medicines']))
        self.total_stockists_value.setText(str(stats['total_stockists']))
        self.total_savings_value.setText(f"₹{stats['total_savings']:,.2f}")
        self.avg_savings_value.setText(f"₹{stats['avg_savings']:,.2f}")
        
        # Update total purchases
        self.total_purchases_label.setText(f"Total Purchases: {stats['total_purchases']}")
        self.total_saved_label.setText(f"Total Money Saved: ₹{stats['total_savings']:,.2f}")
        
        # Update best deals list
        self.best_deals_list.clear()
        for deal in stats['best_deals']:
            item = QListWidgetItem()
            widget = self.create_deal_item(deal)
            item.setSizeHint(widget.sizeHint())
            self.best_deals_list.addItem(item)
            self.best_deals_list.setItemWidget(item, widget)
        
        # Update recent medicines
        self.recent_medicines_list.clear()
        for med in stats['recent_medicines']:
            item = QListWidgetItem(f"💊 {med['medicine_name']} - {med['company_name']}")
            self.recent_medicines_list.addItem(item)
    
    def create_deal_item(self, deal):
        """Create a custom widget for best deals list"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)
        
        name_label = QLabel(f"💊 {deal['medicine_name']}")
        name_label.setObjectName("dealName")
        
        price_label = QLabel(f"₹{deal['price']:.2f}")
        price_label.setObjectName("dealPrice")
        
        savings_label = QLabel(f"Save ₹{deal['savings']:.2f}")
        savings_label.setObjectName("dealSavings")
        
        stockist_label = QLabel(f"at {deal['stockist_name']}")
        stockist_label.setObjectName("dealStockist")
        
        layout.addWidget(name_label)
        layout.addStretch()
        layout.addWidget(price_label)
        layout.addWidget(savings_label)
        layout.addWidget(stockist_label)
        
        return widget
    
    def perform_search(self):
        """Perform medicine search"""
        search_term = self.search_input.text()
        
        if len(search_term) < 2:
            QMessageBox.warning(self, "Search", "Please enter at least 2 characters")
            return
        
        results = self.controller.search_medicines(search_term)
        
        if not results:
            QMessageBox.information(self, "Search", "No medicines found")
            self.results_table.hide()
            return
        
        self.results_table.show()
        self.results_table.setRowCount(len(results))
        
        for row, med in enumerate(results):
            self.results_table.setItem(row, 0, QTableWidgetItem(med['medicine_name']))
            self.results_table.setItem(row, 1, QTableWidgetItem(med['company_name']))
            self.results_table.setItem(row, 2, QTableWidgetItem(med['stockist_name']))
            self.results_table.setItem(row, 3, QTableWidgetItem(f"₹{med['mrp']:.2f}"))
            self.results_table.setItem(row, 4, QTableWidgetItem(f"₹{med['final_price']:.2f}"))
            self.results_table.setItem(row, 5, QTableWidgetItem(f"₹{med['savings']:.2f}"))
            
            # Color code savings
            if med['savings'] > 0:
                self.results_table.item(row, 5).setForeground(QColor(40, 167, 69))
    
    def apply_styles(self):
        """Apply custom styles"""
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            #headerFrame {
                background-color: white;
                border-radius: 20px;
                padding: 20px;
            }
            
            #welcomeLabel {
                color: #4CAF50;
                font-size: 14px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            #mainTitle {
                font-size: 28px;
                font-weight: 700;
                color: #1a2634;
            }
            
            #subTitle {
                font-size: 14px;
                color: #6c757d;
                margin-top: 5px;
            }
            
            #dateLabel {
                font-size: 14px;
                color: #495057;
                font-weight: 600;
                padding: 10px 15px;
                background-color: #f8f9fa;
                border-radius: 10px;
            }
            
            #statCard {
                background-color: white;
                border-radius: 15px;
                padding: 15px;
            }
            
            #statTitle {
                color: #6c757d;
                font-size: 14px;
            }
            
            #statValue {
                font-size: 28px;
                font-weight: 700;
                color: #1a2634;
            }
            
            #searchGroup {
                background-color: white;
                border-radius: 15px;
                padding: 20px;
                margin-top: 10px;
            }
            
            #searchGroup::title {
                color: #1a2634;
                font-size: 16px;
                font-weight: 600;
                padding-left: 10px;
            }
            
            QLineEdit {
                border: 2px solid #e9ecef;
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 14px;
                background-color: white;
            }
            
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
            
            #searchButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 600;
                padding: 10px 25px;
            }
            
            #searchButton:hover {
                background-color: #45a049;
            }
            
            #resultsTable {
                border: none;
                border-radius: 10px;
                background-color: white;
                margin-top: 15px;
            }
            
            #resultsTable::item {
                padding: 10px;
            }
            
            #resultsTable QHeaderView::section {
                background-color: #f8f9fa;
                padding: 12px;
                border: none;
                font-weight: 600;
                color: #495057;
            }
            
            #bestDealsFrame, #recentFrame, #quickStatsFrame {
                background-color: white;
                border-radius: 15px;
                padding: 20px;
            }
            
            #sectionTitle {
                font-size: 18px;
                font-weight: 600;
                color: #1a2634;
                margin-bottom: 15px;
            }
            
            #bestDealsList, #recentList {
                border: none;
                background-color: transparent;
            }
            
            #bestDealsList::item, #recentList::item {
                padding: 8px;
                border-bottom: 1px solid #f0f2f5;
            }
            
            #dealName {
                font-weight: 600;
                color: #1a2634;
            }
            
            #dealPrice {
                color: #4CAF50;
                font-weight: 700;
                padding: 0 10px;
            }
            
            #dealSavings {
                color: #28a745;
                background-color: #d4edda;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
            }
            
            #dealStockist {
                color: #6c757d;
                font-size: 12px;
            }
            
            #actionButton {
                background-color: white;
                border: 2px solid #4CAF50;
                border-radius: 12px;
                color: #4CAF50;
                font-size: 14px;
                font-weight: 600;
                padding: 10px 25px;
            }
            
            #actionButton:hover {
                background-color: #4CAF50;
                color: white;
            }
            
            QGroupBox {
                font-weight: 600;
                border: 2px solid #e9ecef;
                border-radius: 15px;
                margin-top: 15px;
                padding-top: 15px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
            }
        """)