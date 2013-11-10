#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, flask, os, codecs

app = flask.Flask(__name__)

@app.route("/")
def main():
    return flask.render_template("index.html")

@app.route("/challenge")
def challenge():
    return flask.render_template("challenge.html")

@app.route("/response")
def response():
    return flask.render_template("response.html")

@app.route("/battle")
def battle():
    return flask.render_template("battle.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

