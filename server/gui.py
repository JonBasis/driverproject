import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QListWidget, QTabWidget, QMessageBox, QStatusBar,
                            QGroupBox, QGridLayout, QSplitter, QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon

from DeviceIoControl.DeviceHandler import DeviceHandler

DEVICE_NAME = r"\\.\driver"

class DriverGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.device_handler = None
        self.init_ui()
        self.connect_to_driver()
        
    def init_ui(self):
        self.setWindowTitle("NetGuard - Driver Control Center")
        self.setMinimumSize(900, 600)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a12;
            }
            QTabWidget::pane {
                border: 1px solid #3a3a5a;
                background-color: #1a1a2a;
            }
            QTabBar::tab {
                background-color: #252538;
                color: #ccccdd;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3a3a5a;
                color: #00ccff;
            }
            QPushButton {
                background-color: #2a2a3a;
                color: #cccccc;
                border: 1px solid #3a3a5a;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a3a5a;
                border: 1px solid #5a5a7a;
            }
            QPushButton:pressed {
                background-color: #1a1a2a;
            }
            QLineEdit {
                background-color: #2a2a3a;
                color: #cccccc;
                border: 1px solid #3a3a5a;
                border-radius: 4px;
                padding: 8px;
            }
            QListWidget {
                background-color: #1a1a2a;
                color: #cccccc;
                border: 1px solid #3a3a5a;
                border-radius: 4px;
                padding: 4px;
            }
            QLabel {
                color: #cccccc;
            }
            QGroupBox {
                border: 1px solid #3a3a5a;
                border-radius: 4px;
                margin-top: 1em;
                color: #00ccff;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        header = QWidget()
        header_layout = QHBoxLayout(header)
        title_label = QLabel("NETGUARD FIREWALL")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: #00ccff;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        main_layout.addWidget(header)
        
        self.connection_status = QLabel("Driver Status: Disconnected")
        self.connection_status.setAlignment(Qt.AlignCenter)
        self.connection_status.setStyleSheet("color: #cc3333;")
        main_layout.addWidget(self.connection_status)
        
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        ip_tab = QWidget()
        ip_layout = QVBoxLayout(ip_tab)
        
        ip_block_group = QGroupBox("IP Address Control")
        ip_block_layout = QGridLayout(ip_block_group)
        
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter IP address (e.g., 192.168.1.1)")
        
        self.block_ip_btn = QPushButton("Block IP")
        self.block_ip_btn.clicked.connect(self.block_ip)
        self.block_ip_btn.setStyleSheet("background-color: #cc3333;")
        
        self.unblock_ip_btn = QPushButton("Unblock IP")
        self.unblock_ip_btn.clicked.connect(self.unblock_ip)
        self.unblock_ip_btn.setStyleSheet("background-color: #33cc33;")
        
        ip_block_layout.addWidget(QLabel("IP Address:"), 0, 0)
        ip_block_layout.addWidget(self.ip_input, 0, 1)
        ip_block_layout.addWidget(self.block_ip_btn, 0, 2)
        ip_block_layout.addWidget(self.unblock_ip_btn, 0, 3)
        
        ip_list_group = QGroupBox("Blocked IP Addresses")
        ip_list_layout = QVBoxLayout(ip_list_group)
        
        self.ip_list = QListWidget()
        refresh_ip_btn = QPushButton("Refresh List")
        refresh_ip_btn.clicked.connect(self.refresh_ip_list)
        
        ip_list_layout.addWidget(self.ip_list)
        ip_list_layout.addWidget(refresh_ip_btn)
        
        ip_layout.addWidget(ip_block_group)
        ip_layout.addWidget(ip_list_group)
        
        port_tab = QWidget()
        port_layout = QVBoxLayout(port_tab)
        
        port_block_group = QGroupBox("Port Control")
        port_block_layout = QGridLayout(port_block_group)
        
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Enter port number (0-65535)")
        
        self.block_port_btn = QPushButton("Block Port")
        self.block_port_btn.clicked.connect(self.block_port)
        self.block_port_btn.setStyleSheet("background-color: #cc3333;")
        
        self.unblock_port_btn = QPushButton("Unblock Port")
        self.unblock_port_btn.clicked.connect(self.unblock_port)
        self.unblock_port_btn.setStyleSheet("background-color: #33cc33;")
        
        port_block_layout.addWidget(QLabel("Port Number:"), 0, 0)
        port_block_layout.addWidget(self.port_input, 0, 1)
        port_block_layout.addWidget(self.block_port_btn, 0, 2)
        port_block_layout.addWidget(self.unblock_port_btn, 0, 3)
        
        port_list_group = QGroupBox("Blocked Ports")
        port_list_layout = QVBoxLayout(port_list_group)
        
        self.port_list = QListWidget()
        refresh_port_btn = QPushButton("Refresh List")
        refresh_port_btn.clicked.connect(self.refresh_port_list)
        
        port_list_layout.addWidget(self.port_list)
        port_list_layout.addWidget(refresh_port_btn)
        
        port_layout.addWidget(port_block_group)
        port_layout.addWidget(port_list_group)
        
        test_tab = QWidget()
        test_layout = QVBoxLayout(test_tab)
        
        test_group = QGroupBox("Driver Test")
        test_group_layout = QVBoxLayout(test_group)
        
        self.test_input = QLineEdit()
        self.test_input.setPlaceholderText("Enter a message to send to the driver")
        self.test_btn = QPushButton("Test Driver")
        self.test_btn.clicked.connect(self.test_driver)
        self.test_output = QLabel("Response will appear here")
        self.test_output.setStyleSheet("background-color: #1a1a2a; padding: 10px; border-radius: 4px;")
        self.test_output.setAlignment(Qt.AlignCenter)
        self.test_output.setWordWrap(True)
        
        test_group_layout.addWidget(QLabel("Test Message:"))
        test_group_layout.addWidget(self.test_input)
        test_group_layout.addWidget(self.test_btn)
        test_group_layout.addWidget(QLabel("Driver Response:"))
        test_group_layout.addWidget(self.test_output)
        
        test_layout.addWidget(test_group)
        
        tab_widget.addTab(ip_tab, "IP Control")
        tab_widget.addTab(port_tab, "Port Control")
        tab_widget.addTab(test_tab, "Driver Test")
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def connect_to_driver(self):
        try:
            self.status_bar.showMessage("Connecting to driver...")
            self.device_handler = DeviceHandler(DEVICE_NAME)
            self.connection_status.setText("Driver Status: Connected")
            self.connection_status.setStyleSheet("color: #33cc33;")
            self.status_bar.showMessage("Connected to driver successfully")
            
            self.refresh_ip_list()
            self.refresh_port_list()
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect to driver: {str(e)}")
            self.status_bar.showMessage("Failed to connect to driver")
    
    def block_ip(self):
        if not self.device_handler:
            QMessageBox.warning(self, "Not Connected", "Not connected to driver")
            return
        
        ip = self.ip_input.text().strip()
        if not ip:
            QMessageBox.warning(self, "Input Error", "Please enter an IP address")
            return
        
        try:
            success = self.device_handler.block_ip(ip)
            if success:
                self.status_bar.showMessage(f"IP {ip} blocked successfully")
                self.refresh_ip_list()
            else:
                QMessageBox.warning(self, "Block Error", f"Failed to block IP {ip}")
        except Exception as e:
            QMessageBox.critical(self, "Block Error", f"Error blocking IP: {str(e)}")
    
    def unblock_ip(self):
        if not self.device_handler:
            QMessageBox.warning(self, "Not Connected", "Not connected to driver")
            return
        
        ip = self.ip_input.text().strip()
        if not ip:
            QMessageBox.warning(self, "Input Error", "Please enter an IP address")
            return
        
        try:
            success = self.device_handler.unblock_ip(ip)
            if success:
                self.status_bar.showMessage(f"IP {ip} unblocked successfully")
                self.refresh_ip_list()
            else:
                QMessageBox.warning(self, "Unblock Error", f"Failed to unblock IP {ip}")
        except Exception as e:
            QMessageBox.critical(self, "Unblock Error", f"Error unblocking IP: {str(e)}")
    
    def block_port(self):
        if not self.device_handler:
            QMessageBox.warning(self, "Not Connected", "Not connected to driver")
            return
        
        port = self.port_input.text().strip()
        if not port:
            QMessageBox.warning(self, "Input Error", "Please enter a port number")
            return
        
        try:
            success = self.device_handler.block_port(port)
            if success:
                self.status_bar.showMessage(f"Port {port} blocked successfully")
                self.refresh_port_list()
            else:
                QMessageBox.warning(self, "Block Error", f"Failed to block port {port}")
        except Exception as e:
            QMessageBox.critical(self, "Block Error", f"Error blocking port: {str(e)}")
    
    def unblock_port(self):
        if not self.device_handler:
            QMessageBox.warning(self, "Not Connected", "Not connected to driver")
            return
        
        port = self.port_input.text().strip()
        if not port:
            QMessageBox.warning(self, "Input Error", "Please enter a port number")
            return
        
        try:
            success = self.device_handler.unblock_port(port)
            if success:
                self.status_bar.showMessage(f"Port {port} unblocked successfully")
                self.refresh_port_list()
            else:
                QMessageBox.warning(self, "Unblock Error", f"Failed to unblock port {port}")
        except Exception as e:
            QMessageBox.critical(self, "Unblock Error", f"Error unblocking port: {str(e)}")
    
    def refresh_ip_list(self):
        if not self.device_handler:
            return
        
        try:
            self.ip_list.clear()
            blocked_ips = self.device_handler.enum_ip()
            if blocked_ips:
                for ip in blocked_ips:
                    self.ip_list.addItem(ip)
            self.status_bar.showMessage("IP list refreshed")
        except Exception as e:
            QMessageBox.critical(self, "Refresh Error", f"Error refreshing IP list: {str(e)}")
    
    def refresh_port_list(self):
        if not self.device_handler:
            return
        
        try:
            self.port_list.clear()
            blocked_ports = self.device_handler.enum_port()
            if blocked_ports:
                for port in blocked_ports:
                    self.port_list.addItem(str(port))
            self.status_bar.showMessage("Port list refreshed")
        except Exception as e:
            QMessageBox.critical(self, "Refresh Error", f"Error refreshing port list: {str(e)}")
    
    def test_driver(self):
        if not self.device_handler:
            QMessageBox.warning(self, "Not Connected", "Not connected to driver")
            return
        
        message = self.test_input.text()
        if not message:
            QMessageBox.warning(self, "Input Error", "Please enter a test message")
            return
        
        try:
            response = self.device_handler.test_driver(message)
            if response:
                self.test_output.setText(response)
                self.status_bar.showMessage("Driver test completed")
            else:
                self.test_output.setText("No response from driver")
        except Exception as e:
            QMessageBox.critical(self, "Test Error", f"Error testing driver: {str(e)}")
            self.test_output.setText(f"Error: {str(e)}")

def main():
    app = QApplication(sys.argv)
    
    # Set application-wide styles for a futuristic look
    app.setStyle("Fusion")
    
    # Dark palette for futuristic look
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(13, 13, 18))
    dark_palette.setColor(QPalette.WindowText, QColor(204, 204, 220))
    dark_palette.setColor(QPalette.Base, QColor(26, 26, 42))
    dark_palette.setColor(QPalette.AlternateBase, QColor(42, 42, 58))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    dark_palette.setColor(QPalette.ToolTipText, QColor(204, 204, 220))
    dark_palette.setColor(QPalette.Text, QColor(204, 204, 220))
    dark_palette.setColor(QPalette.Button, QColor(42, 42, 58))
    dark_palette.setColor(QPalette.ButtonText, QColor(204, 204, 220))
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(0, 204, 255))
    dark_palette.setColor(QPalette.Highlight, QColor(0, 153, 204))
    dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(dark_palette)
    
    window = DriverGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()