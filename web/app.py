from flask import Flask, redirect, render_template, session, request
import socket
import json

state = 0

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')


@app.route('/btn_click')
def btn_click():
	global state
	state = request.args['vis_index']
	return 'Success'


@app.route('/get_settings', methods=['GET'])
def get_settings():
	return json.dumps({'vis_index': state})


if __name__ == '__main__':
	app.run(host='0.0.0.0')