
from twilio.rest import Client
import random
from django.conf import settings

def generate_otp():
    return str(random.randint(100000, 999999))


def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(phone_number):
    otp = generate_otp()
    
    
    try:
        # message = client.messages.create(
        #     body=f"Your OTP is {otp}",
        #     from_="7558009441",
        #     to=f"+91{phone_number}"  # Add country code prefix properly
        # )
        return {"status": "success", "otp": "000000", "sid": "hi"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
