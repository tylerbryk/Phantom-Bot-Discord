from flask import Flask
from threading import Thread

app = Flask('PhantomBot')
@app.route('/')

def main():
		return "Bot online!"

def run():
    app.run(host="0.0.0.0", port=8080)

def start():
    server = Thread(target=run)
    server.start()