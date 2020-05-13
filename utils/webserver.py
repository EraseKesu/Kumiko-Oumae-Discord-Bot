from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def main():
    return "Hackbot: OK Webserver: OK TO DO LIST: <br /> <br /> " """<iframe width="560" height="315" src="https://www.youtube.com/embed/pKkrCHnun0M" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>"""

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()