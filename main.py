import time
import random
from modules.whatsapp_handler import WhatsAppHandler
from modules.product_handler import ProductHandler
from modules.invoice_generator import InvoiceGenerator
from config import SHOP_NAME, SHOP_LOGO_PATH, INVOICES_FOLDER, DISCOUNT_MIN_QTY, DISCOUNT_PERCENT

def process_order(message_text, customer_phone):
    # SIMPLE PARSER: Expects "Order: item_id=PK101 qty=2"
    try:
        parts = message_text.split()
        item_id = parts[1].split('=')[1]
        qty = int(parts[2].split('=')[1])
        return item_id, qty
    except:
        return None, None

def run_bot():
    # Initialize all handlers
    whatsapp = WhatsAppHandler()
    products = ProductHandler("data/products.csv")
    invoices = InvoiceGenerator(SHOP_NAME, SHOP_LOGO_PATH, INVOICES_FOLDER)
    
    whatsapp.start_driver()
    if not whatsapp.open_whatsapp():
        return

    print("🤖 Bot is active and listening...")

    while True:
        # 1. Listen for new messages (This is the part you'll expand with Selenium scrapers)
        # For now, let's pretend we found an order:
        mock_msg = "Order: item_id=PK101 qty=3" 
        customer_phone = "+94701595851" # Use your test number

        item_id, qty = process_order(mock_msg, customer_phone)
        
        if item_id:
            # 2. Check Product & Stock
            product = products.get_product(item_id)
            if product and products.check_stock(item_id, qty):
                
                # 3. Calculate Total & Discount
                subtotal = product['price'] * qty
                discount = 0
                if qty >= DISCOUNT_MIN_QTY:
                    discount = subtotal * (DISCOUNT_PERCENT / 100)
                
                grand_total = subtotal - discount
                
                # 4. Generate Invoice
                invoice_path = invoices.generate(
                    order_id=random.randint(1000, 9999),
                    customer_name="Valued Customer",
                    items=[{'name': product['name'], 'price': product['price'], 'qty': qty}],
                    total=grand_total,
                    discount=discount
                )
                
                # 5. Send confirmation and file
                whatsapp.send_message(customer_phone, f"Order confirmed! Your total is: {grand_total}")
                # (Note: You'll need a separate function in whatsapp_handler to attach files)
                
                # 6. Update Stock
                products.update_stock(item_id, qty)
                
        time.sleep(60) # Wait 1 minute before checking again

if __name__ == "__main__":
    run_bot()
