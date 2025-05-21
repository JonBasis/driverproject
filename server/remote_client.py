from NetworkingWrappers.Client import Client
import datetime
from datetime import datetime
from NetworkingWrappers.ProtocolMessages.ProtocolMessage import ProtocolMessage

SERVER_IP : str = "127.0.0.1"
SERVER_PORT : int = 12345

DEBUG = True

PASSWORD : bytes = b'123456789012345678901234'

def debug_print(message : str) -> None:
    if DEBUG:
        print(f"[{datetime.now()}], {message}")
    

def identify_to_server(client_object : Client, client_id : int, password : str) -> bool:
    verify_message : ProtocolMessage = ProtocolMessage("IDENTIFY", status="admin")
    client_object.send_message(verify_message)

    verify_ack_message : ProtocolMessage = client_object.recv_message()
    if verify_ack_message.get_code() == "ERROR":
        print(verify_ack_message.get_value("error_code"), verify_ack_message.get_value("error"))
        return False
    
    elif verify_ack_message.get_code() != "ACKIDENTIFY":
        return False
    
    auth_message : ProtocolMessage = ProtocolMessage("AUTH", id=client_id, password=password)
    client_object.send_message(auth_message)

    auth_ack_message : ProtocolMessage = client_object.recv_message()
    if auth_ack_message.get_code() == "ACKAUTH":
        return True
    
    elif auth_ack_message.get_code() == "ERROR":
        print(auth_ack_message.get_value("error_code"), auth_ack_message.get_value("error"))
        return False
    
    return False


def block_ip(client_object : Client, driver_id : int, ip : str) -> bool:
    block_ip_message : ProtocolMessage = ProtocolMessage("BLOCKIP", driver_id=driver_id, ip=ip)
    client_object.send_message(block_ip_message)

    response : ProtocolMessage = client_object.recv_message()
    if response.get_code() == "ERROR":
        print("error", response.get_value("error_code"), response.get_value("error"))
        return False
    if response.get_code() != "ACKCOMMAND":
        print(f"error, expected getting ACKCOMMAND, got {response.get_code()} instead")
        return False
    
    success : bool = response.get_value("success")
    print(f"block ip success: {success}")

    return success


def unblock_ip(client_object : Client, driver_id : int, ip : str) -> bool:
    unblock_ip_message : ProtocolMessage = ProtocolMessage("UNBLOCKIP", driver_id=driver_id, ip=ip)
    client_object.send_message(unblock_ip_message)

    response : ProtocolMessage = client_object.recv_message()
    if response.get_code() == "ERROR":
        print("error", response.get_value("error_code"), response.get_value("error"))
        return False
    if response.get_code() != "ACKCOMMAND":
        print(f"error, expected getting ACKCOMMAND, got {response.get_code()} instead")
        return False
    
    success : bool = response.get_value("success")
    print(f"block ip success: {success}")

    return success


def block_port(client_object : Client, driver_id : int, port : int) -> bool:
    block_port_message : ProtocolMessage = ProtocolMessage("BLOCKPORT", driver_id=driver_id, port=port)
    client_object.send_message(block_port_message)

    response : ProtocolMessage = client_object.recv_message()
    if response.get_code() == "ERROR":
        print("error", response.get_value("error_code"), response.get_value("error"))
        return False
    if response.get_code() != "ACKCOMMAND":
        print(f"error, expected getting ACKCOMMAND, got {response.get_code()} instead")
        return False
    
    success : bool = response.get_value("success")
    print(f"block ip success: {success}")

    return success


def unblock_port(client_object : Client, driver_id : int, port : int) -> bool:
    unblock_port_message : ProtocolMessage = ProtocolMessage("UNBLOCKPORT", driver_id=driver_id, port=port)
    client_object.send_message(unblock_port_message)

    response : ProtocolMessage = client_object.recv_message()
    if response.get_code() == "ERROR":
        print("error", response.get_value("error_code"), response.get_value("error"))
        return False
    if response.get_code() != "ACKCOMMAND":
        print(f"error, expected getting ACKCOMMAND, got {response.get_code()} instead")
        return False
    
    success : bool = response.get_value("success")
    print(f"block ip success: {success}")

    return success


def convert_int_to_ip(int_ip : int) -> str:
    return f"{str(int_ip >> 24)}.{str((int_ip >> 16) & 0xff)}.{str((int_ip >> 8) & 0xff)}.{str(int_ip & 0xff)}"


def enum_ip(client_object : Client, driver_id : int) -> list[str, int]:
    enum_ip_message : ProtocolMessage = ProtocolMessage("ENUMIP", driver_id=driver_id)
    client_object.send_message(enum_ip_message)

    response : ProtocolMessage = client_object.recv_message()
    if response.get_code() == "ERROR":
        print("error", response.get_value("error_code"), response.get_value("error"))
        return None
    if response.get_code() != "ENUMIPR":
        print(f"error, expected getting ENUMIPR, got {response.get_code()} instead")
        return None
    
    ip_array : list[int, int] = response.get_value("ip_array")
    ip_array = [(convert_int_to_ip(ip), count) for ip, count in ip_array]
    print("ip_array", ip_array)
    return ip_array


def enum_port(client_object : Client, driver_id : int) -> list[int, int]:
    enum_port_message : ProtocolMessage = ProtocolMessage("ENUMPORT", driver_id=driver_id)
    client_object.send_message(enum_port_message)

    response : ProtocolMessage = client_object.recv_message()
    if response.get_code() == "ERROR":
        print("error", response.get_value("error_code"), response.get_value("error"))
        return None
    if response.get_code() != "ENUMPORTR":
        print(f"error, expected getting ENUMPORTR, got {response.get_code()} instead")
        return None
    
    port_array : list[int, int] = response.get_value("port_array")

    return port_array


def add_admin(client_object : Client, admin_id : int, password : str) -> bool:
    add_admin_message : ProtocolMessage = ProtocolMessage("ADDADMIN", id=admin_id, password=password)
    client_object.send_message(add_admin_message)

    response : ProtocolMessage = client_object.recv_message()
    if response.get_code() == "ERROR":
        print("error", response.get_value("error_code"), response.get_value("error"))
        return False
    if response.get_code() != "ACKCOMMAND":
        print(f"error, expected getting ACKCOMMAND, got {response.get_code()} instead")
        return False
    
    success : bool = response.get_value("success")
    print(f"block ip success: {success}")

    return success


def add_driver(client_object : Client, driver_id : int, password : str) -> bool:
    add_driver_message : ProtocolMessage = ProtocolMessage("ADDDRIVER", id=driver_id, password=password)
    client_object.send_message(add_driver_message)

    response : ProtocolMessage = client_object.recv_message()
    if response.get_code() == "ERROR":
        print("error", response.get_value("error_code"), response.get_value("error"))
        return False
    if response.get_code() != "ACKCOMMAND":
        print(f"error, expected getting ACKCOMMAND, got {response.get_code()} instead")
        return False
    
    success : bool = response.get_value("success")
    print(f"block ip success: {success}")

    return success


def close(client_object : Client):
    close_message : ProtocolMessage = ProtocolMessage("CLOSE")
    client_object.send_message(close_message)



# def handle_driver(client_object : Client):
#     while True:
#         pass


# def main() -> None:
#     client_object : Client = Client(DEBUG, SERVER_IP, SERVER_PORT)

#     print("welcome!")
    
#     success : bool = client_object.handshake()
#     if not success:
#         print("handshake failed")
#         return
    
#     client_id : int = int(input("id:"))
#     password : str = input("password:")
#     success : bool = identify_to_server(client_object, client_id, password)

#     if not success:
#         return
    
#     handle_driver(client_object)
        
#     print("goodbye!")

# if __name__ == '__main__':
#     main()

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QListWidget, QTabWidget, QMessageBox, QStatusBar,
                            QGroupBox, QGridLayout, QSplitter, QFrame, QInputDialog,
                            QDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon

from NetworkingWrappers.Client import Client
from NetworkingWrappers.ProtocolMessages.ProtocolMessage import ProtocolMessage
# Import the functions from remote_client.py

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.client = None
        self.admin_id = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("DriverShark - Login")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #0a0a12;
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
            QLineEdit {
                background-color: #2a2a3a;
                color: #cccccc;
                border: 1px solid #3a3a5a;
                border-radius: 4px;
                padding: 8px;
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
        """)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("DRIVERSHARK REMOTE CLIENT")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #00ccff;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Server connection group
        server_group = QGroupBox("Server Connection")
        server_layout = QVBoxLayout(server_group)
        
        self.status_label = QLabel("Server Status: Disconnected")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #cc3333;")
        
        connect_btn = QPushButton("Connect to Server")
        connect_btn.clicked.connect(self.connect_to_server)
        
        server_layout.addWidget(self.status_label)
        server_layout.addWidget(connect_btn)
        
        layout.addWidget(server_group)
        
        # Login group
        login_group = QGroupBox("Authentication")
        login_layout = QGridLayout(login_group)
        
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter your admin ID")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        login_layout.addWidget(QLabel("Admin ID:"), 0, 0)
        login_layout.addWidget(self.id_input, 0, 1)
        login_layout.addWidget(QLabel("Password:"), 1, 0)
        login_layout.addWidget(self.password_input, 1, 1)
        
        layout.addWidget(login_group)
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        login_btn.setStyleSheet("background-color: #33cc33;")
        layout.addWidget(login_btn)
        
        self.status_message = QLabel("")
        self.status_message.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_message)
        
    def connect_to_server(self):
        try:
            self.status_message.setText("Connecting to server...")
            self.client = Client(True, SERVER_IP, SERVER_PORT)
            
            success = self.client.handshake()
            if not success:
                QMessageBox.critical(self, "Connection Error", "Handshake with server failed")
                self.status_message.setText("Failed to complete handshake with server")
                return
            
            self.status_label.setText("Server Status: Connected")
            self.status_label.setStyleSheet("color: #33cc33;")
            self.status_message.setText("Connected to server successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect to server: {str(e)}")
            self.status_message.setText("Failed to connect to server")
    
    def login(self):
        if not self.client:
            QMessageBox.warning(self, "Not Connected", "Please connect to the server first")
            return
        
        client_id_text = self.id_input.text().strip()
        password = self.password_input.text().strip()
        
        if not client_id_text or not password:
            QMessageBox.warning(self, "Input Error", "Please enter all required fields")
            return
        
        try:
            client_id = int(client_id_text)
            
            success = identify_to_server(self.client, client_id, password)
            if not success:
                QMessageBox.warning(self, "Authentication Error", "Authentication failed")
                return
            
            self.admin_id = client_id
            self.accept()  # Close dialog with accept result
            
        except ValueError:
            QMessageBox.warning(self, "Input Error", "ID field must be an integer")
        except Exception as e:
            QMessageBox.critical(self, "Login Error", f"Error during login: {str(e)}")

class RemoteClientGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = None
        self.admin_id = None
        self.init_ui()
        
    def init_ui(self):
        """ Initialize GUI """
        self.setWindowTitle("DriverShark - Remote Client")
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
        title_label = QLabel("DRIVERSHARK REMOTE CLIENT")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: #00ccff;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        main_layout.addWidget(header)
        
        # Connection status display
        self.connection_status = QLabel("Connected as Admin ID: None")
        self.connection_status.setAlignment(Qt.AlignCenter)
        self.connection_status.setStyleSheet("color: #33cc33;")
        main_layout.addWidget(self.connection_status)
        
        # Tab widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # IP Tab
        ip_tab = QWidget()
        ip_layout = QVBoxLayout(ip_tab)
        
        ip_block_group = QGroupBox("IP Address Control")
        ip_block_layout = QGridLayout(ip_block_group)
        
        self.ip_driver_id = QLineEdit()
        self.ip_driver_id.setPlaceholderText("Enter target driver ID")
        
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter IP address (e.g., 192.168.1.1)")
        
        self.block_ip_btn = QPushButton("Block IP")
        self.block_ip_btn.clicked.connect(self.handle_block_ip)
        self.block_ip_btn.setStyleSheet("background-color: #cc3333;")
        
        self.unblock_ip_btn = QPushButton("Unblock IP")
        self.unblock_ip_btn.clicked.connect(self.handle_unblock_ip)
        self.unblock_ip_btn.setStyleSheet("background-color: #33cc33;")
        
        ip_block_layout.addWidget(QLabel("Driver ID:"), 0, 0)
        ip_block_layout.addWidget(self.ip_driver_id, 0, 1)
        ip_block_layout.addWidget(QLabel("IP Address:"), 1, 0)
        ip_block_layout.addWidget(self.ip_input, 1, 1)
        ip_block_layout.addWidget(self.block_ip_btn, 1, 2)
        ip_block_layout.addWidget(self.unblock_ip_btn, 1, 3)
        
        ip_list_group = QGroupBox("Blocked IP Addresses")
        ip_list_layout = QVBoxLayout(ip_list_group)
        
        ip_list_header = QHBoxLayout()
        self.enum_ip_driver_id = QLineEdit()
        self.enum_ip_driver_id.setPlaceholderText("Enter driver ID to view its blocked IPs")
        refresh_ip_btn = QPushButton("Refresh List")
        refresh_ip_btn.clicked.connect(self.handle_refresh_ip_list)
        
        ip_list_header.addWidget(QLabel("Driver ID:"))
        ip_list_header.addWidget(self.enum_ip_driver_id)
        ip_list_header.addWidget(refresh_ip_btn)
        
        self.ip_list = QListWidget()
        
        ip_list_layout.addLayout(ip_list_header)
        ip_list_layout.addWidget(self.ip_list)
        
        ip_layout.addWidget(ip_block_group)
        ip_layout.addWidget(ip_list_group)
        
        # Port Tab
        port_tab = QWidget()
        port_layout = QVBoxLayout(port_tab)
        
        port_block_group = QGroupBox("Port Control")
        port_block_layout = QGridLayout(port_block_group)
        
        self.port_driver_id = QLineEdit()
        self.port_driver_id.setPlaceholderText("Enter target driver ID")
        
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Enter port number (0-65535)")
        
        self.block_port_btn = QPushButton("Block Port")
        self.block_port_btn.clicked.connect(self.handle_block_port)
        self.block_port_btn.setStyleSheet("background-color: #cc3333;")
        
        self.unblock_port_btn = QPushButton("Unblock Port")
        self.unblock_port_btn.clicked.connect(self.handle_unblock_port)
        self.unblock_port_btn.setStyleSheet("background-color: #33cc33;")
        
        port_block_layout.addWidget(QLabel("Driver ID:"), 0, 0)
        port_block_layout.addWidget(self.port_driver_id, 0, 1)
        port_block_layout.addWidget(QLabel("Port Number:"), 1, 0)
        port_block_layout.addWidget(self.port_input, 1, 1)
        port_block_layout.addWidget(self.block_port_btn, 1, 2)
        port_block_layout.addWidget(self.unblock_port_btn, 1, 3)
        
        port_list_group = QGroupBox("Blocked Ports")
        port_list_layout = QVBoxLayout(port_list_group)
        
        port_list_header = QHBoxLayout()
        self.enum_port_driver_id = QLineEdit()
        self.enum_port_driver_id.setPlaceholderText("Enter driver ID to view its blocked ports")
        refresh_port_btn = QPushButton("Refresh List")
        refresh_port_btn.clicked.connect(self.handle_refresh_port_list)
        
        port_list_header.addWidget(QLabel("Driver ID:"))
        port_list_header.addWidget(self.enum_port_driver_id)
        port_list_header.addWidget(refresh_port_btn)
        
        self.port_list = QListWidget()
        
        port_list_layout.addLayout(port_list_header)
        port_list_layout.addWidget(self.port_list)
        
        port_layout.addWidget(port_block_group)
        port_layout.addWidget(port_list_group)
        
        # Admin Tab
        admin_tab = QWidget()
        admin_layout = QVBoxLayout(admin_tab)
        
        admin_group = QGroupBox("Admin Management")
        admin_layout_grid = QGridLayout(admin_group)
        
        add_admin_btn = QPushButton("Add New Admin")
        add_admin_btn.clicked.connect(self.handle_add_admin)
        
        add_driver_btn = QPushButton("Add New Driver")
        add_driver_btn.clicked.connect(self.handle_add_driver)
        
        admin_layout_grid.addWidget(add_admin_btn, 0, 0)
        admin_layout_grid.addWidget(add_driver_btn, 0, 1)
        
        admin_layout.addWidget(admin_group)
        admin_layout.addStretch()
        
        # Add tabs to tab widget
        tab_widget.addTab(ip_tab, "IP Control")
        tab_widget.addTab(port_tab, "Port Control")
        tab_widget.addTab(admin_tab, "Admin")
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def set_client(self, client, admin_id):
        """Set the client and admin ID after successful login"""
        self.client = client
        self.admin_id = admin_id
        self.connection_status.setText(f"Connected as Admin ID: {admin_id}")
    
    def handle_block_ip(self):
        """Block an IP address"""
        if not self.client:
            QMessageBox.warning(self, "Not Connected", "Not connected or not authenticated")
            return
        
        driver_id_text = self.ip_driver_id.text().strip()
        ip = self.ip_input.text().strip()
        
        if not driver_id_text or not ip:
            QMessageBox.warning(self, "Input Error", "Please enter all required fields")
            return
        
        try:
            driver_id = int(driver_id_text)
            success = block_ip(self.client, driver_id, ip)
            if success:
                self.status_bar.showMessage(f"IP {ip} blocked successfully for driver {driver_id}")
            else:
                QMessageBox.warning(self, "Block Error", f"Failed to block IP {ip}")
                
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Driver ID must be an integer")
        except Exception as e:
            QMessageBox.critical(self, "Block Error", f"Error blocking IP: {str(e)}")
    
    def handle_unblock_ip(self):
        """Unblock an IP address"""
        if not self.client:
            QMessageBox.warning(self, "Not Connected", "Not connected or not authenticated")
            return
        
        driver_id_text = self.ip_driver_id.text().strip()
        ip = self.ip_input.text().strip()
        
        if not driver_id_text or not ip:
            QMessageBox.warning(self, "Input Error", "Please enter all required fields")
            return
        
        try:
            driver_id = int(driver_id_text)
            success = unblock_ip(self.client, driver_id, ip)
            if success:
                self.status_bar.showMessage(f"IP {ip} unblocked successfully for driver {driver_id}")
            else:
                QMessageBox.warning(self, "Unblock Error", f"Failed to unblock IP {ip}")
                
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Driver ID must be an integer")
        except Exception as e:
            QMessageBox.critical(self, "Unblock Error", f"Error unblocking IP: {str(e)}")
    
    def handle_block_port(self):
        """Block a port"""
        if not self.client:
            QMessageBox.warning(self, "Not Connected", "Not connected or not authenticated")
            return
        
        driver_id_text = self.port_driver_id.text().strip()
        port_text = self.port_input.text().strip()
        
        if not driver_id_text or not port_text:
            QMessageBox.warning(self, "Input Error", "Please enter all required fields")
            return
        
        try:
            driver_id = int(driver_id_text)
            port = int(port_text)
            success = block_port(self.client, driver_id, port)
            if success:
                self.status_bar.showMessage(f"Port {port} blocked successfully for driver {driver_id}")
            else:
                QMessageBox.warning(self, "Block Error", f"Failed to block port {port}")
                
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Driver ID and port must be integers")
        except Exception as e:
            QMessageBox.critical(self, "Block Error", f"Error blocking port: {str(e)}")
    
    def handle_unblock_port(self):
        """Unblock a port"""
        if not self.client:
            QMessageBox.warning(self, "Not Connected", "Not connected or not authenticated")
            return
        
        driver_id_text = self.port_driver_id.text().strip()
        port_text = self.port_input.text().strip()
        
        if not driver_id_text or not port_text:
            QMessageBox.warning(self, "Input Error", "Please enter all required fields")
            return
        
        try:
            driver_id = int(driver_id_text)
            port = int(port_text)
            success = unblock_port(self.client, driver_id, port)
            if success:
                self.status_bar.showMessage(f"Port {port} unblocked successfully for driver {driver_id}")
            else:
                QMessageBox.warning(self, "Unblock Error", f"Failed to unblock port {port}")
                
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Driver ID and port must be integers")
        except Exception as e:
            QMessageBox.critical(self, "Unblock Error", f"Error unblocking port: {str(e)}")
    
    def handle_refresh_ip_list(self):
        """Refresh the list of blocked IPs"""
        if not self.client:
            return
        
        driver_id_text = self.enum_ip_driver_id.text().strip()
        if not driver_id_text:
            QMessageBox.warning(self, "Input Error", "Please enter a driver ID")
            return
        
        try:
            driver_id = int(driver_id_text)
            ip_array = enum_ip(self.client, driver_id)
            
            self.ip_list.clear()
            if ip_array:
                for ip, count in ip_array:
                    self.ip_list.addItem(f"{ip.ljust(16, ' ')} (blocked {count} times)")
            
            self.status_bar.showMessage(f"IP list refreshed for driver {driver_id}")
            
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Driver ID must be an integer")
        except Exception as e:
            QMessageBox.critical(self, "Refresh Error", f"Error refreshing IP list: {str(e)}")
    
    def handle_refresh_port_list(self):
        """Refresh the list of blocked ports"""
        if not self.client:
            return
        
        driver_id_text = self.enum_port_driver_id.text().strip()
        if not driver_id_text:
            QMessageBox.warning(self, "Input Error", "Please enter a driver ID")
            return
        
        try:
            driver_id = int(driver_id_text)
            port_array = enum_port(self.client, driver_id)
            
            self.port_list.clear()
            if port_array:
                for port, count in port_array:
                    self.port_list.addItem(f"{str(port).ljust(16, ' ')} (blocked {count} times)")
            
            self.status_bar.showMessage(f"Port list refreshed for driver {driver_id}")
            
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Driver ID must be an integer")
        except Exception as e:
            QMessageBox.critical(self, "Refresh Error", f"Error refreshing port list: {str(e)}")
    
    def handle_add_admin(self):
        """Add a new admin"""
        if not self.client:
            QMessageBox.warning(self, "Not Connected", "Not connected to server")
            return
        
        admin_id, ok1 = QInputDialog.getInt(self, "New Admin", "Enter admin ID:", 1000, 1, 9999)
        if not ok1:
            return
            
        password, ok2 = QInputDialog.getText(self, "New Admin", "Enter admin password:", QLineEdit.Password)
        if not ok2 or not password:
            return
        
        try:
            success = add_admin(self.client, admin_id, password)
            if success:
                self.status_bar.showMessage(f"Admin ID {admin_id} added successfully")
                QMessageBox.information(self, "Success", f"Admin ID {admin_id} added successfully")
            else:
                QMessageBox.warning(self, "Add Admin Error", f"Failed to add admin")
                
        except Exception as e:
            QMessageBox.critical(self, "Add Admin Error", f"Error adding admin: {str(e)}")
    
    def handle_add_driver(self):
        """Add a new driver"""
        if not self.client:
            QMessageBox.warning(self, "Not Connected", "Not connected to server")
            return
        
        driver_id, ok1 = QInputDialog.getInt(self, "New Driver", "Enter driver ID:", 1000, 1, 9999)
        if not ok1:
            return
            
        password, ok2 = QInputDialog.getText(self, "New Driver", "Enter driver password:", QLineEdit.Password)
        if not ok2 or not password:
            return
        
        try:
            success = add_driver(self.client, driver_id, password)
            if success:
                self.status_bar.showMessage(f"Driver ID {driver_id} added successfully")
                QMessageBox.information(self, "Success", f"Driver ID {driver_id} added successfully")
            else:
                QMessageBox.warning(self, "Add Driver Error", f"Failed to add driver")
                
        except Exception as e:
            QMessageBox.critical(self, "Add Driver Error", f"Error adding driver: {str(e)}")
    
    def closeEvent(self, event):
        """Handle window closing event"""
        if self.client:
            try:
                close(self.client)
            except:
                pass
        event.accept()

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
    
    # First, show login dialog
    login_dialog = LoginDialog()
    if login_dialog.exec_() != QDialog.Accepted:
        # User cancelled or failed to login
        sys.exit(0)
        
    # If we reach here, login was successful
    window = RemoteClientGUI()
    window.set_client(login_dialog.client, login_dialog.admin_id)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()