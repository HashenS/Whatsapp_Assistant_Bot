from fpdf import FPDF
import os
from datetime import datetime

class InvoiceGenerator:
    def __init__(self, shop_name, logo_path, shop_phone, save_dir):
        self.shop_name = shop_name
        self.logo_path = logo_path
        self.shop_phone = shop_phone 
        self.save_dir = save_dir

    def generate(self, order_id, customer_name, items, total, discount, shipping=0, tracking_id="N/A", delivery_date="N/A", status="UNPAID"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=False)
        pdf.add_page()
        
        # --- 0. BACKGROUND WATERMARK ---
        # Draw this first so it stays in the background
        if status.upper() == "PAID":
            watermark_text = "PAID"
            pdf.set_text_color(200, 255, 200) # Ghostly Green
        else:
            watermark_text = "UNPAID"
            pdf.set_text_color(255, 200, 200) # Ghostly Red

        pdf.set_font("Arial", 'B', 100)
        with pdf.rotation(45, x=105, y=150):
            # Centering roughly: A4 is 210mm wide. 
            # We offset x to center the large text
            pdf.text(45, 160, watermark_text)
        
        # Reset color to black for everything else
        pdf.set_text_color(0, 0, 0)

        # --- 1. PREMIUM HEADER (Dark Background) ---
        pdf.set_fill_color(127, 0, 255)  # Violet
        pdf.rect(0, 0, 210, 40, 'F')
        
        # Logo (if exists)
        if os.path.exists(self.logo_path):
            pdf.image(self.logo_path, 10, 8, 25)
        
        # Contact Info in White
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_y(15)
        pdf.cell(0, 10, f"Contact: {self.shop_phone}", ln=True, align='R')
        
        # --- 2. ORDER INFORMATION ---
        pdf.set_text_color(0, 0, 0)
        pdf.set_y(45)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(100, 10, f"BILL TO: {customer_name}", ln=False)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 10, f"INVOICE #: {order_id}", ln=True, align='R')
        pdf.cell(0, 5, f"DATE: {datetime.now().strftime('%B %d, %Y')}", ln=True, align='R')
        
        # Tracking & Delivery Info
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"TRACKING ID: {tracking_id}", ln=True, align='R')
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 5, f"EXPECTED DELIVERY: {delivery_date}", ln=True, align='R')
        
        # --- 3. TABLE HEADER ---
        pdf.ln(5)
        pdf.set_text_color(0, 0, 0)
        pdf.set_fill_color(236, 240, 241) # Light Silver
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(90, 10, "  PRODUCT DESCRIPTION", 0, 0, 'L', True)
        pdf.cell(30, 10, "PRICE", 0, 0, 'C', True)
        pdf.cell(30, 10, "QTY", 0, 0, 'C', True)
        pdf.cell(40, 10, "TOTAL", 0, 1, 'R', True)

        # --- 4. ITEM ROWS ---
        pdf.set_font("Arial", '', 10)
        for i, item in enumerate(items):
            fill = i % 2 == 0
            if fill: pdf.set_fill_color(250, 250, 250)
            
            pdf.cell(90, 12, f"  {item['name']}", 0, 0, 'L', fill)
            pdf.cell(30, 12, f"{item['price']:,}", 0, 0, 'C', fill)
            pdf.cell(30, 12, str(item['qty']), 0, 0, 'C', fill)
            pdf.cell(40, 12, f"Rs. {item['price'] * item['qty']:,}", 0, 1, 'R', fill)

        # --- 5. SUMMARY SECTION ---
        pdf.ln(5)
        pdf.set_font("Arial", '', 10)
        pdf.cell(150, 8, "Subtotal:", 0, 0, 'R')
        pdf.cell(40, 8, f"Rs. {total - shipping + discount:,}", 0, 1, 'R')
        
        pdf.set_text_color(231, 76, 60) # Red for Discount
        pdf.cell(150, 8, f"Discount:", 0, 0, 'R')
        pdf.cell(40, 8, f"- Rs. {discount:,}", 0, 1, 'R')

        pdf.set_text_color(0, 0, 0)
        pdf.cell(150, 8, "Shipping Charge:", 0, 0, 'R')
        pdf.cell(40, 8, f"Rs. {shipping:,}", 0, 1, 'R')
        
        pdf.ln(2)
        pdf.set_text_color(44, 62, 80)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(150, 10, "GRAND TOTAL:", 0, 0, 'R')
        pdf.cell(40, 10, f"Rs. {total:,.2f}", 0, 1, 'R')

        # --- 6. FOOTER ---
        pdf.set_y(-30)
        pdf.set_font("Arial", 'I', 9)
        pdf.set_text_color(127, 140, 141)
        pdf.cell(0, 10, "Thank you for shopping with EXORA! We appreciate your business.", 0, 1, 'C')
        pdf.cell(0, 5, "If you have any questions, contact us on WhatsApp.", 0, 1, 'C')

        # Save file
        file_path = os.path.join(self.save_dir, f"Invoice_{order_id}.pdf")
        pdf.output(file_path)
        return file_path
