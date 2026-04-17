import os
from dotenv import load_dotenv


load_dotenv()

WABA_ID = os.getenv("WABA_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERSION = os.getenv("WHATSAPP_VERSION")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ADMIN_NUMBER = os.getenv("ADMIN_NUMBER")
BANK_DETAILS = os.getenv("BANK_DETAILS")
# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INVOICES_FOLDER = os.path.join(BASE_DIR, "data", "invoices")
LOG_FOLDER = os.path.join(BASE_DIR, "logs")

# Create necessary folders
os.makedirs(INVOICES_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

# WhatsApp Settings
WHATSAPP_SESSION_PATH = os.path.join(BASE_DIR, "whatsapp_session")

# Shop Information

SHOP_NAME = "EXORA"
SHOP_ADDRESS = "Kegalle, Sri Lanka"
SHOP_PHONE = "+94701595851"
SHOP_LOGO_PATH = "C:/Projects/Whatsapp-order-bot/assets/logo.png"

# Discount Configuration
DISCOUNT_PERCENT = 5
DISCOUNT_MIN_QTY = 3

# Shipping Config
SHIPPING_RATES = {
    'colombo': 200,
    'kandy': 350,
    'other': 500
}
EXCEL_FILE_PATH = os.path.join(BASE_DIR, "data", "orders.xlsx")

print("✅ Config loaded successfully!")