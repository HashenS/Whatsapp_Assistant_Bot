import requests
from config import ACCESS_TOKEN, PHONE_NUMBER_ID, VERSION, WABA_ID
import os

class WhatsAppHandler:
    def __init__(self):
        self.url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
        self.headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

    def send_template_message(self, recipient_number, template_name="hello_world"):
        # Use this for sending the first message to a customer
        data = {
            "messaging_product": "whatsapp",
            "to": recipient_number.replace('+', '').replace(' ', ''),
            "type": "text", # or "template" as shown in screenshot
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "en_US"}
            }
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        return response.json()

    def send_text_message(self, recipient_number, message_text):
        # Use this to reply to a customer once they have messaged you first
        data = {
            "messaging_product": "whatsapp",
            "to": recipient_number.replace('+', '').replace(' ', ''),
            "type": "text",
            "text": {"body": message_text}
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        return response.json()
    


    def send_document(self, recipient_number, file_path, caption="Your Invoice"):
        # Use PHONE_NUMBER_ID here!
        upload_url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/media"
        
        print(f"📤 Attempting to upload: {file_path}")
        
        files = {
            'file': (os.path.basename(file_path), open(file_path, 'rb'), 'application/pdf'),
        }
        data = {
            'messaging_product': 'whatsapp',
            'type': 'application/pdf' 
        }
        
        upload_response = requests.post(upload_url, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}, files=files, data=data)
        
        # DEBUG: Print exactly what Meta says about the upload
        print("Meta Upload Response:", upload_response.json())
        
        media_id = upload_response.json().get('id')

        # 2. Send the document
        if media_id:
            print(f"✅ Upload success! Media ID: {media_id}. Sending to {recipient_number}...")
            send_url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient_number.replace('+', '').replace(' ', ''),
                "type": "document",
                "document": {
                    "id": media_id,
                    "filename": os.path.basename(file_path),
                    "caption": caption
                }
            }
            response = requests.post(send_url, headers=self.headers, json=payload)
            print("Meta Send Response:", response.json())
            return response.json()
        else:
            print("❌ Upload FAILED. Check the 'Meta Upload Response' above for the reason.")
            return {"error": "Upload failed"}
    def send_image_by_id(self, recipient_number, image_id, caption="New Receipt"):
        """Sends an image that is already on Meta's server using its ID"""
        data = {
            "messaging_product": "whatsapp",
            "to": recipient_number.replace('+', '').replace(' ', ''),
            "type": "image",
            "image": {
                "id": image_id,
                "caption": caption
            }
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        return response.json()

    def send_image_by_id(self, recipient_number, image_id, caption="New Receipt"):
        """Sends an image that is already on Meta's server using its ID"""
        data = {
            "messaging_product": "whatsapp",
            "to": recipient_number.replace('+', '').replace(' ', ''),
            "type": "image",
            "image": {
                "id": image_id,
                "caption": caption
            }
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        return response.json()
