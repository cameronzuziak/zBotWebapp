# Set up a free trial twilio account, and create a phone number.
# for set up help see https://www.twilio.com/docs/iam/keys/api-key 
TWILIO_ACCOUNT = 'Twilio Account Number'
TWILIO_TOKEN = 'Twilio Token'
TWILIO_NUMBER ='Twilio Number'


# BinanceUS API keys for the server, for info on how to create API keys see https://www.binance.com/en/support/faq/360002502072  
# This key is used for queryiing historical trade data for chart functionality. Once user enters their own API keys
# then user keys are used for chart functionality
BINANCE_API_KEY = "Serve Key"
BINANCE_SEC_KEY = "Secret Key"

# Encryption Key for encryption of user API keys, must be in byte array.
ENCRYPTION_KEY = b''

# Url to your database, see sqlalchemy docs for formatting details specific to sql dialect https://docs.sqlalchemy.org/en/14/dialects/index.html 
DB_URL = ""


