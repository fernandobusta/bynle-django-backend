from django.conf import settings

import os
import io
import random
import string
import stripe
import qrcode
from datetime import datetime
from decouple import config
from PIL import Image



def get_time():
    # Get the current date and time
    current_datetime = datetime.now()

    # Get the timestamp from the current date and time
    timestamp = int(current_datetime.timestamp())
    return timestamp

stripe.api_key = settings.STRIPE_SECRET_KEY 

def ticketQRCodeGenerator(ticket_id):
    """https://medium.com/@rahulmallah785671/create-qr-code-by-using-python-2370d7bd9b8d#:~:text=To%20create%20a%20QR%20code,a%20text%20or%20a%20URL."""
    # Create a QR code object
    qr = qrcode.QRCode(version=1, box_size=10, border=5)    
    # Define the data to be encoded in the QR code
    data = "{}/validate-ticket/{}/".format(config('DJANGO_URL'), ticket_id)

    # Add the data to the QR code object
    qr.add_data(data)

    # Make the QR code
    qr.make(fit=True)

    # Create an image from the QR code with a black fill color and white background
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert the PIL Image to a file-like object
    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)

    return img_io

def ticketCodeGenerator():
    # Generate a random string of length 6

    letters = string.ascii_lowercase
    numbers = string.digits
    code1 = ''.join(random.choice(letters + numbers) for i in range(6))
    code2 = ''.join(random.choice(letters + numbers) for i in range(6))
    code3 = ''.join(random.choice(letters + numbers) for i in range(6))
    return code1 + '-' + code2 + '-' + code3

def get_stripe_accountid(user_email):
        accounts = stripe.Account.list()
        # Loop through the accounts and print email for each
        for n in range(len(accounts.data)):
            email = accounts.data[n]["email"]
            if user_email == email:
                # Return a tuple containing True and the Stripe account ID
                return True
        return False

def stripe_tos_acceptance(account_id):
            time = get_time()
            stripe.Account.modify(
                account_id,
                tos_acceptance={"date": time, "ip": "8.8.8.8"},
                )
        
def create_account_custom(context):
        account = stripe.Account.create(
            type="custom",
            country="IE",
            email=context['user_email'],
            business_type="individual",
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
            business_profile={"url": "https://bynle.com", "mcc": "7922"},
        )
        return account.id

def create_account_express(context):
        account = stripe.Account.create(
            type="express",
            country="IE",
            email=context['user_email'],
            business_type="individual",
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
            business_profile={"url": "https://bynle.com", "mcc": "7922"},
        )
        return account.id


def calculate_application_fee(price):
    fee = int(price * .1)
    return fee

def account_create_link(account_id, club_id):
        account_link_response = stripe.AccountLink.create(
            account=account_id,
            refresh_url=config('FRONTEND_URL'),
            return_url=config('FRONTEND_URL') + "/stripe-successful/" + str(club_id),
            type="account_onboarding",
            collection_options={"fields": "eventually_due"},
        )
        return account_link_response

def account_create_link_user(account_id, user_id):
        account_link_response = stripe.AccountLink.create(
            account=account_id,
            refresh_url=config('FRONTEND_URL'),
            return_url=config('FRONTEND_URL') + "/stripe-successful/user/" + str(user_id),
            type="account_onboarding",
            collection_options={"fields": "eventually_due"},
        )
        return account_link_response

def get_stripe_account_completion(account_id):
    info = stripe.Account.retrieve(account_id)
    return info["payouts_enabled"]
