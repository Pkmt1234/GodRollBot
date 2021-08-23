#makes sure the bot keeps running 24/7
from replit import db
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return str(db["leaderboardprint"])

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()