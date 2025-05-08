import mysql.connector
from mysql.connector import Error
import hashlib
import os
import json

config = {
    'host' : 'localhost',
    'user' : 'drivershark',
    'password' : 'drivershark'
}

pepper : str = 'driversharkpepper'

class DBHandler:
    HASH_SALT_SIZE : int = 32
    
    def connect(self) -> None:
        """ connect to db and create a cursor object """

        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor()
        except Error as e:
            print(f"error connecting to db: {e}")
            raise
    
    def setup_tables(self) -> None:
        """ setup db tables """

        try:
            print("creating tables")

            self.cursor.execute("CREATE DATABASE IF NOT EXISTS drivershark")
            self.cursor.execute("USE drivershark")

            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS drivers(
                id int NOT NULL PRIMARY KEY,
                password_hash varchar(255) NOT NULL,
                password_salt varchar(255) NOT NULL,
                blocked_ips JSON DEFAULT ('[]'),
                blocked_ports JSON DEFAULT ('[]')
            )
            """)

            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins(
                id int NOT NULL PRIMARY KEY,
                password_hash varchar(255) NOT NULL,
                password_salt varchar(255) NOT NULL
            )
            """)

            self.conn.commit()

            print("tables created")
        
        except Error as e:
            print(f"error creating tables: {e}")
            raise
        
    def __init__(self) -> None:
        self.config = config
        self.conn = None
        self.cursor = None
        self.connect()
        self.setup_tables()
    
    def __del__(self) -> None:
        if self.conn:
            self.conn.close()
    
    def _hash_password(self, password : str, salt = None) -> tuple[str, str]:
        """ hash password with salt and pepper and return hashed password and salt """

        if not salt:
            salt : str = os.urandom(DBHandler.HASH_SALT_SIZE).hex()
        salted_peppered_password : str = password + pepper + salt
        password_hash : str = hashlib.sha256(salted_peppered_password.encode()).hexdigest()

        return password_hash, salt
    
    def add_driver(self, driver_id : int, driver_password : str) -> bool:
        """ add driver to db """

        try:
            password_hash, salt = self._hash_password(driver_password)

            self.cursor.execute("""
            INSERT INTO drivers (id, password_hash, password_salt) VALUES (%s, %s, %s)
            """, (driver_id, password_hash, salt))
            self.conn.commit()
            return True
        except Error as e:
            print(f"error adding driver to db: {e}")
            self.conn.rollback()
            return False
    
    def remove_driver(self, driver_id : int) -> bool:
        """ remove driver from db """
        
        try:
            self.cursor.execute("""
            DELETE FROM drivers WHERE id = %s
            """, (driver_id,))
            self.conn.commit()
            return True
        except Error as e:
            print(f"error removed driver from db: {e}")
            self.conn.rollback()
            return False
    
    def get_driver(self, driver_id : int):
        """ get driver from db """

        try:
            self.cursor.execute("""
            SELECT * FROM drivers WHERE id = %s
            """, (driver_id, ))
            driver = self.cursor.fetchone()
            columns = [column[0] for column in self.cursor.description]
            if driver:
                driver = dict(zip(columns, driver))
                driver['blocked_ips'] = json.loads(driver['blocked_ips'])
                driver['blocked_ports'] = json.loads(driver['blocked_ports'])
            
            return driver
        except Error as e:
            print(f"error getting driver from db: {e}")
            return None
    
    def verify_driver(self, driver_id : int, password : str) -> bool:
        """ verify driver id and password """

        driver_entry = self.get_driver(driver_id)

        if not driver_entry:
            return False
        
        password_hash : str = driver_entry['password_hash']
        salt : str = driver_entry['password_salt']
        
        return password_hash == self._hash_password(password, salt)[0]
    
    
    def _set_driver_blocked_ips(self, driver_id : int, blocked_ips : list[int]) -> bool:
        """ set driver blocked ips to input in db """

        try:
            self.cursor.execute("""
            UPDATE drivers SET blocked_ips = %s WHERE id = %s
            """, (json.dumps(blocked_ips), driver_id))

            self.conn.commit()
            return True
        except Error as e:
            print(f"error setting driver blocked ips: {e}")
            self.conn.rollback()
            return False
    
    def _set_driver_blocked_ports(self, driver_id : int, blocked_ports : list[int]) -> bool:
        """ set driver blocked ports to input in db """

        try:
            self.cursor.execute("""
                UPDATE drivers SET blocked_ports = %s WHERE id = %s
                """, (json.dumps(blocked_ports), driver_id))
            
            self.conn.commit()
            return True
        except Error as e:
            print(f"error setting driver blocked ports: {e}")
            self.conn.rollback()
            return False
    
    
    def _ip_in_array(self, blocked_ips : list[int], ip : int) -> bool:
        """ check if ip is in array """

        low = 0
        high = len(blocked_ips) - 1
        middle = None
        
        if len(blocked_ips) == 0:
            return False
        
        while low <= high:
            middle = low + (high - low) // 2

            if blocked_ips[middle] < ip:
                low = middle + 1
            
            elif blocked_ips[middle] > ip:
                high = middle - 1
            
            else:
                return True
        
        return False
    
    def block_ip(self, driver_id : int, ip : int) -> bool:
        """ add ip to blocked_ips """

        driver_entry = self.get_driver(driver_id)
        if not driver_entry:
            return False
        
        blocked_ips : list[int] = driver_entry['blocked_ips']

        if not self._ip_in_array(blocked_ips, ip):
            blocked_ips.append(ip)
            blocked_ips.sort()
            return self._set_driver_blocked_ips(driver_id, blocked_ips)
        
        return True
    
    def unblock_ip(self, driver_id : int, ip : int) -> bool:
        """ remove ip from blocked_ips """

        driver_entry = self.get_driver(driver_id)
        if not driver_entry:
            return False
        
        blocked_ips : list[int] = driver_entry['blocked_ips']

        if self._ip_in_array(blocked_ips, ip):
            blocked_ips.remove(ip)
            return self._set_driver_blocked_ips(driver_id, blocked_ips)
        
        return True
    
    def block_port(self, driver_id : int, port : int) -> bool:
        """ add port to blocked_ports """

        driver_entry = self.get_driver(driver_id)
        if not driver_entry:
            return False
        
        blocked_ports : list[int] = driver_entry['blocked_ports']

        if not self._ip_in_array(blocked_ports, port):
            blocked_ports.append(port)
            blocked_ports.sort()
            return self._set_driver_blocked_ports(driver_id, blocked_ports)
        
        return True
    
    def unblock_port(self, driver_id : int, port : int) -> bool:
        """ remove port from blocked_ports """

        driver_entry = self.get_driver(driver_id)
        if not driver_entry:
            return False
        
        blocked_ports : list[int] = driver_entry['blocked_ports']

        if self._ip_in_array(blocked_ports, port):
            blocked_ports.remove(port)
            return self._set_driver_blocked_ports(driver_id, blocked_ports)
        
        return True
    
    def get_blocked_ips(self, driver_id : int) -> list[int]:
        """ get blocked_ips array """

        driver_entry = self.get_driver(driver_id)
        if not driver_entry:
            return None
        
        blocked_ips : list[int] = driver_entry['blocked_ips']
        return blocked_ips
    
    def get_blocked_ports(self, driver_id : int) -> list[int]:
        """ get blocked_ports array """

        driver_entry = self.get_driver(driver_id)
        if not driver_entry:
            return None
        
        blocked_ports : list[int] = driver_entry['blocked_ports']
        return blocked_ports
    
    def add_admin(self, admin_id : int, admin_password : str) -> bool:
        """ add admin to db """

        try:
            password_hash, salt = self._hash_password(admin_password)
            self.cursor.execute("""
            INSERT INTO admins (id, password_hash, password_salt) VALUES (%s, %s, %s)
            """, (admin_id, password_hash, salt))
            self.conn.commit()
            return True
        except Error as e:
            print(f"error adding admin: {e}")
            return False
    
    def get_admin(self, admin_id : int):
        """ get admin from db """

        try:
            self.cursor.execute("""
            SELECT * FROM admins WHERE id = %s
            """, (admin_id, ))

            admin = self.cursor.fetchone()
            columns = [column[0] for column in self.cursor.description]
            if not admin:
                return admin
            admin_dict = dict(zip(columns, admin))
            return admin_dict
        except Error as e:
            print(f"error getting admin from db: {e}")
            return None
    
    def verify_admin(self, admin_id : int, password : str) -> bool:
        """ verify admin id and password """
        
        admin_entry = self.get_admin(admin_id)
        
        if not admin_entry:
            return False
        
        password_hash : str = admin_entry['password_hash']
        salt : str = admin_entry['password_salt']

        return password_hash == self._hash_password(password, salt)[0]