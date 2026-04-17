import openpyxl
from openpyxl import Workbook
import os
from datetime import datetime

class OrderLogger:
    def __init__(self, file_path):
        self.file_path = file_path
        self._initialize_excel()

    def _initialize_excel(self):
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
        if not os.path.exists(self.file_path):
            wb = Workbook()
            ws = wb.active
            ws.title = "Orders"
            # Define Headers based on Client Requirements
            headers = [
                "Order ID", 
                "Date", 
                "Customer Name", 
                "Product Name", 
                "Qty", 
                "Subtotal", 
                "Discount Amount", 
                "Shipping Charge", 
                "Total Amount", 
                "Tracking Number", 
                "Payment Status",
                "Delivery Status"
            ]
            ws.append(headers)
            wb.save(self.file_path)
            print(f"✅ Excel database initialized: {self.file_path}")

    def log_order(self, order_data):
        """
        Appends a new order row to the Excel file.
        order_data: list of values matching the header structure.
        """
        try:
            wb = openpyxl.load_workbook(self.file_path)
            ws = wb.active
            ws.append(order_data)
            wb.save(self.file_path)
            return True
        except Exception as e:
            print(f"❌ Excel Logging Error: {e}")
            return False
