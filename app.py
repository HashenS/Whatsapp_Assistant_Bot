from flask import Flask, request, jsonify
import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import re

# Import your own modules
from modules.product_handler import ProductHandler
from modules.invoice_generator import InvoiceGenerator
from modules.whatsapp_handler import WhatsAppHandler
from modules.order_logger import OrderLogger
from config import (
    SHOP_NAME, SHOP_LOGO_PATH, INVOICES_FOLDER, 
    DISCOUNT_MIN_QTY, DISCOUNT_PERCENT, VERIFY_TOKEN, 
    SHOP_PHONE, SHIPPING_RATES, EXCEL_FILE_PATH,
    ADMIN_NUMBER, BANK_DETAILS
)

load_dotenv()
app = Flask(__name__)

# The "Notebook" to remember conversations
USER_SESSIONS = {}

# Initialize your "Workers"
product_db = ProductHandler("data/products.csv")
invoice_maker = InvoiceGenerator(SHOP_NAME, SHOP_LOGO_PATH, SHOP_PHONE, INVOICES_FOLDER)
whatsapp = WhatsAppHandler()
order_logger = OrderLogger(EXCEL_FILE_PATH)

def parse_template(text):
    """Parses 'Item id = PK101 qty = 2 dist = Colombo' using Regex"""
    try:
        item_id = re.search(r"Item id\s*=\s*(\w+)", text, re.I).group(1).upper()
        qty = int(re.search(r"qty\s*=\s*(\d+)", text, re.I).group(1))
        # Look for district word characters (can include letters)
        district = re.search(r"dist\s*=\s*([a-zA-Z]+)", text, re.I).group(1).lower()
        return item_id, qty, district
    except Exception as e:
        print(f"❌ Parsing Error: {e}")
        return None, None, None

@app.route('/webhook', methods=['GET'])
def verify():
    token = request.args.get("hub.verify_token")
    mode = request.args.get("hub.mode")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    response = jsonify({"status": "success"}), 200

    try:
        entry = data.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})
        
        if 'messages' in value:
            msg_obj = value['messages'][0]
            sender_num = msg_obj['from']
            msg_type = msg_obj.get('type')
            
            # --- CONTEXT: Get Current User Session ---
            session = USER_SESSIONS.get(sender_num, {"state": "IDLE"})
            
            # --- 1. HANDLE TEXT MESSAGES ---
            if msg_type == 'text':
                text_body = msg_obj.get('text', {}).get('body', '')
                print(f"📩 Text from {sender_num}: {text_body}")

                # SPECIAL: Admin Commands
                if sender_num == ADMIN_NUMBER and text_body.lower().startswith("/approve"):
                    try:
                        customer_num = text_body.split()[1]
                        cust_session = USER_SESSIONS.get(customer_num)
                        
                        if cust_session and cust_session['state'] == 'PENDING_APPROVAL':
                            order = cust_session['order_data']
                            
                            # Generate FINAL PAID PDF
                            pdf_path = invoice_maker.generate(
                                order['id'], "Customer", 
                                [{'name': order['name'], 'price': order['price'], 'qty': order['qty']}], 
                                order['total'], order['discount'], order['shipping'], 
                                order['tracking'], order['delivery_date'], status="PAID"
                            )
                            
                            # Send to Customer
                            whatsapp.send_text_message(customer_num, "🎉 *Payment Verified!* Your order is being processed.\nHere is your final invoice.")
                            whatsapp.send_document(customer_num, pdf_path, caption=f"Paid_Invoice_{order['id']}")
                            
                            # Log to Excel
                            order_logger.log_order([
                                order['id'], datetime.now().strftime('%Y-%m-%d'), "Customer",
                                order['name'], order['qty'], order['subtotal'], order['discount'],
                                order['shipping'], order['total'], order['tracking'], "PAID", "Pending"
                            ])
                            
                            # Deduct Stock
                            product_db.update_stock(order['item_id'], order['qty'])
                            
                            # Clear Session
                            USER_SESSIONS.pop(customer_num)
                            whatsapp.send_text_message(ADMIN_NUMBER, f"✅ Approved & Sent to {customer_num}")
                        else:
                            whatsapp.send_text_message(ADMIN_NUMBER, "❌ No pending order found for this number.")
                    except:
                        whatsapp.send_text_message(ADMIN_NUMBER, "❌ Usage: /approve <phone_number>")
                    return response

                # STATE: IDLE -> Send Template OR Help Message
                if session["state"] == "IDLE":
                    # If they say a starting word:
                    if any(x in text_body.lower() for x in ["hi", "hello", "order", "help"]):
                        template = (
                            "Welcome to EXORA! 👗\n\nPlease fill this template and send it back:\n\n"
                            "Item id = \nqty = \ndist = \n\n"
                            "Example:\nItem id = PK101\nqty = 2\ndist = Colombo"
                        )
                        whatsapp.send_text_message(sender_num, template)
                        USER_SESSIONS[sender_num] = {"state": "AWAITING_ORDER"}
                    
                    # --- NEW: THE FALLBACK ---
                    else:
                        help_msg = ("Welcome to EXORA Assistant! 🛍️\n\n"
                                   "I'm ready to help you with your order. Please reply with *'Hi'* or *'Order'* to get started!")
                        whatsapp.send_text_message(sender_num, help_msg)

                # STATE: AWAITING_ORDER -> Send Summary
                elif session["state"] == "AWAITING_ORDER":
                    item_id, qty, dist = parse_template(text_body)
                    product = product_db.get_product(item_id) if item_id else None
                    
                    if product and product_db.check_stock(item_id, qty):
                        order_id = random.randint(1000, 9999)
                        subtotal = product['price'] * qty
                        discount = (subtotal * (DISCOUNT_PERCENT/100)) if qty >= DISCOUNT_MIN_QTY else 0
                        shipping = SHIPPING_RATES.get(dist, SHIPPING_RATES['other'])
                        total = subtotal - discount + shipping
                        tracking = f"EX-{random.randint(100000, 999999)}"
                        delivery = (datetime.now() + timedelta(days=3)).strftime('%B %d, %Y')
                        
                        USER_SESSIONS[sender_num].update({
                            "state": "AWAITING_CONFIRMATION",
                            "order_data": {
                                "id": order_id, "item_id": item_id, "name": product['name'],
                                "price": product['price'], "qty": qty, "dist": dist,
                                "subtotal": subtotal, "discount": discount, "shipping": shipping,
                                "total": total, "tracking": tracking, "delivery_date": delivery
                            }
                        })
                        
                        summary = (
                            f"🛒 *ORDER SUMMARY*\n"
                            f"Item: {product['name']}\n"
                            f"Qty: {qty}\n"
                            f"Total: Rs. {total:,}\n"
                            f"District: {dist.capitalize()}\n\n"
                            f"Type *YES* to confirm or * to edit."
                        )
                        whatsapp.send_text_message(sender_num, summary)
                    else:
                        whatsapp.send_text_message(sender_num, "❌ Item not found or low stock. Please check the ID and try again.")

                # STATE: AWAITING_CONFIRMATION -> Send Unpaid PDF + Bank Details
                elif session["state"] == "AWAITING_CONFIRMATION":
                    if text_body.lower() == "yes":
                        order = session['order_data']
                        # Generate UNPAID PDF
                        pdf_path = invoice_maker.generate(
                            order['id'], "Customer", 
                            [{'name': order['name'], 'price': order['price'], 'qty': order['qty']}], 
                            order['total'], order['discount'], order['shipping'], 
                            order['tracking'], order['delivery_date'], status="UNPAID"
                        )
                        msg = f"✅ *Summary Confirmed!*\n\nPlease pay to:\n\n{BANK_DETAILS}\n\n*Send the receipt here once finished.*"
                        whatsapp.send_text_message(sender_num, msg)
                        whatsapp.send_document(sender_num, pdf_path, caption=f"Unpaid_Invoice_{order['id']}")
                        USER_SESSIONS[sender_num]["state"] = "AWAITING_PAYMENT"
                    elif text_body == "*":
                        whatsapp.send_text_message(sender_num, "Order cancelled. Type 'order' to start again.")
                        USER_SESSIONS[sender_num] = {"state": "IDLE"}

            # --- 2. HANDLE IMAGE MESSAGES (Receipts) ---
            elif msg_type == 'image':
                # Capture the ID of the image from the customer
                image_id = msg_obj.get('image', {}).get('id')
                print(f"📸 Image from {sender_num}")
                
                if session["state"] == "AWAITING_PAYMENT":
                    # 1. Thank the customer
                    whatsapp.send_text_message(sender_num, "📩 *Receipt Received!* We are verifying your payment now.")
                    USER_SESSIONS[sender_num]["state"] = "PENDING_APPROVAL"
                    
                    # 2. Inform the Admin with the IMAGE included!
                    admin_msg = f"🔔 *NEW RECEIPT*\nFrom: {sender_num}\nOrder ID: {session['order_data']['id']}\n\nType `/approve {sender_num}` to verify."
                    
                    # This sends the PICTURE to YOU with the command in the caption
                    whatsapp.send_image_by_id(ADMIN_NUMBER, image_id, caption=admin_msg)
                else:
                    whatsapp.send_text_message(sender_num, "Welcome to EXORA! 📸 Please say *'Hi'* to start your order before sending a receipt.")

    except Exception as e:
        print(f"⚠️ Webhook Error: {e}")

    return response

if __name__ == "__main__":
    app.run(port=5000, debug=False)
