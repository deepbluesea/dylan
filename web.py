#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, flask, os, codecs
import rhyme

app = flask.Flask(__name__)

@app.route("/")
def main():
    return flask.render_template("index.html")

@app.route("/challenge", methods=['GET', 'POST'])
def challenge():
    if flask.request.method == 'POST':
        challenge = flask.request.form['challenge']
        fire = rhyme.rhyme(flask.request.form['challenge'])
        return flask.render_template("response.html", challenge=challenge, fire=fire)
    return flask.render_template("challenge.html")

@app.route("/battle")
def battle():
    return flask.render_template("battle.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

