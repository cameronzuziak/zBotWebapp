# **********************************
# @author: Cameron Zuziak
# date: 10/22/2021
# Description: algo trader platform for crypto
# **********************************

from enum import unique
from flask import Flask, render_template, url_for, request, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_session import Session
import os, json
from zbot_utils import twil_handler, crypto, binance_handler
from config import *


app = Flask(__name__)
app.secret_key = "Secret Key Goes Here" #can generate using os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(13), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    api_key = db.Column(db.String(200), nullable=True, default="")
    sec_key = db.Column(db.String(200), nullable=True, default="")
    email = db.Column(db.String(80), nullable=True, default="")
    is_running = db.Column(db.Integer, nullable=True, default=0)
    in_position = db.Column(db.Integer, nullable=True, default=0)
    coin_pair = db.Column(db.String(10), nullable=True, default="ADA/USDT")
    rsi_buy = db.Column(db.Integer, nullable=True, default=30)
    rsi_sell = db.Column(db.Integer, nullable=True, default=70)

    def __repr__(self) -> str:
        return '<Welcome %s>' %self.name



# sign up page
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        user_name = request.form['username']
        user_pass = request.form['pass']
        conf_pass = request.form['confpass']
        user_phone = request.form['phone']
        existing_user = Users.query.filter_by(name=user_name).first()
        beta_code = request.form['betacode']
        
        # Check beta test code
        if not beta_code == 'YourBetaTestCode':
            title = "Wrong Beta Test Code"
            return render_template('signup.html', title=title)

        # Check if username is in use
        if not existing_user is None:
            title = "Username In Use"
            return render_template('signup.html', title=title)          

        # check passwords match
        if not user_pass == conf_pass:
            title = "Passwords Don't Match"
            return render_template('signup.html', title=title)
        
        # verify phone is valid mobile phone, not VOIP/landline
        phone_type = twil_handler.verify_phone(user_phone)
        if not phone_type == 'mobile':
            title = "Enter Valid Mobile Phone"
            return render_template('signup.html', title=title)

        # check if phone is in use
        existing_phone = Users.query.filter_by(phone=user_phone).first()
        if not existing_phone is None:
            title = "Phone Already In Use"
            return render_template('signup.html', title=title)          

        # if it passes checks, add user to database
        else:
            try:
                pass_hash = crypto.encrypt(user_pass)
                new_user = Users(
                    name=user_name, 
                    password=pass_hash,
                    phone=user_phone)
                db.session.add(new_user)
                db.session.commit()
                return redirect('/')
            except Exception as e:
                return 'There was an error creating your profile: %s' % e
           
    else:
        title = "Sign Up Here"
        return render_template('signup.html', title=title)

 

# login page
@app.route('/', methods=['POST', 'GET'])
def index():
    session['logged_in'] = False
    if request.method == 'POST':
        user_name = request.form['username']
        user_pass = request.form['pass']
        user_data = Users.query.filter_by(name=user_name).first()

        #check if username is valid
        if user_data is None:
            return render_template('index.html', title="Username doesn't exist")

        pass_hash = user_data.password        
        #check if entered password matches accounts password
        if crypto.verify_hash(pass_hash, user_pass):
            session['id'] = user_data.id
            session['name'] = user_data.name
            session['auth_code'] = str(twil_handler.authenticate(str(user_data.phone)))
            return redirect('/auth')

        else:
            return render_template('index.html', title="Wrong Password")

    else:
        title = "Login Here"
        return render_template('index.html', title=title)



# 2FA using Twilio API for sms
@app.route('/auth', methods=['POST', 'GET'])
def auth():
    if request.method == 'POST':
        auth_code = request.form['code']
        if str(auth_code) == str(session['auth_code']):
            session['logged_in'] = True
            return redirect('/home')
        else:
            return render_template('auth.html', title="wrong code")
    else:
        # remove comment below for prod and comment the statement after
        title = "Enter 6-digit Code"
        #title = str(session['auth_code'])
        return render_template('auth.html', title=title)



# home page
@app.route('/home', methods=['POST', 'GET'])
def home():
    if not session['logged_in'] == True:
        return redirect('/')
    user_data = Users.query.filter_by(id=session['id']).first()
    api_key = user_data.api_key
    sec_key = user_data.sec_key
    if len(api_key) > 1:
        api_key = crypto.fernet_decrypt(api_key)
        sec_key = crypto.fernet_decrypt(sec_key)
        info = binance_handler.get_current_positions(api_key,sec_key)
    else:
        info = [" Add API Keys In Account settings", [{"asset": "Add API Keys", "amnt": 1, "value": 1} ] ]
    title = session['name']
    return render_template('home.html', title=title, info=info)



# seperate endpoint for chart data
@app.route('/home/chart', methods=['POST'])
def chart():
    if not session['logged_in'] == True:
        return redirect('/')

    req = request.get_json()
    user_data = Users.query.filter_by(id=session['id']).first()
    api_key = user_data.api_key
    sec_key = user_data.sec_key
    # if account has their own Binance API key, use accounts keys,
    # if not use server keys. 
    if len(api_key) > 1:
        api_key = crypto.fernet_decrypt(api_key)
        sec_key = crypto.fernet_decrypt(sec_key)
        candles = binance_handler.get_historical_data(api_key,sec_key,req['coin'], req['time_int'])
    else:
        candles = binance_handler.get_historical_data(BINANCE_API_KEY,BINANCE_SEC_KEY,req['coin'], req['time_int'])
    processed_candles = []
    for candle in candles:
        candlestick = {
            "time": candle[0]/1000,
            "open" : candle[1],
            "high" : candle[2],
            "low" : candle[3],
            "close" :candle[4]
        }
        processed_candles.append(candlestick)
    return jsonify(processed_candles) 



# endpoint for bot management
@app.route('/home/bot', methods=['POST'])
def bot():
    if not session['logged_in'] == True:
        return redirect('/')
    req = request.get_json()
    user_data = Users.query.filter_by(id=session['id']).first()
    user_data.is_running = 1
    user_data.in_position = int(req['in_position'])
    user_data.coin_pair = req['coin_pair_bot']
    user_data.rsi_buy = req['rsi_buy']
    user_data.rsi_sell = req['rsi_sell']
    db.session.commit()
    print(req)
    x = {"response": "success"}
    return(x)



# settings page
@app.route('/settings', methods=['POST', 'GET'])
def settings():
    if not session['logged_in'] == True:
        return redirect('/')
    if request.method == 'POST':
        api_key = str(request.form['api_key'])
        sec_key = str(request.form['sec_key'])
        user_pass = request.form['pass']
        user_data = Users.query.filter_by(id=session['id']).first()
        pass_hash = user_data.password        
        #check if password matches
        if crypto.verify_hash(pass_hash, user_pass):
            key_hash = crypto.fernet_encrypt(api_key)
            sec_hash = crypto.fernet_encrypt(sec_key)
            user_data.api_key = key_hash
            user_data.sec_key = sec_hash
            db.session.commit() 
            title = "Keys have been set!"
            return render_template('settings.html', title=title)
        else:
            title = "Wrong Password"
            return render_template('settings.html', title=title)

    else: 
        title = "Set Binance Api Keys"
        return render_template('settings.html', title=title)



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

