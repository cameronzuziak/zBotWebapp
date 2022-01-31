# *****************************
# @author: Cameron Zuziak 
# date: 10/17/2021
# description: this script is just a number of tools 
# built out from twilio api to help with 2FA, verifying phone numbers,
# and messaging users about trading information.
# ******************************

from twilio.rest import Client
import os
import random
from config import TWILIO_TOKEN, TWILIO_ACCOUNT, TWILIO_NUMBER

account_sid = TWILIO_ACCOUNT
account_token = TWILIO_TOKEN
twill_client = Client(account_sid, account_token)


def sms_send(text, client_phone):
    message = twill_client.messages \
                    .create(
                        body=text,
                        from_=TWILIO_NUMBER,
                        to=client_phone
                    )


# verify phone number to ensure it is a valid mobile phone
def verify_phone(client_phone):
    try:
        phone_number = twill_client.lookups.phone_numbers(client_phone).fetch(type=['carrier'])
    except:
        return('Invalid')    
    return(phone_number.carrier.get('type'))


# generate random 6 digit number, and send to user for authentication
def authenticate(phone_num):
    random_id = ''.join([str(random.randint(0, 999)).zfill(3) for _ in range(2)])
    id_send = "zBot Authentication Code: " + random_id
    
    # remove comment on statement below for prod
    sms_send(id_send, phone_num)
    return random_id
