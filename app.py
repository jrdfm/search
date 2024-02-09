#!/usr/bin/python3
# app.py
from flask import Flask, render_template, request
from test import fun  # Import your implementation of the 'fun' function
import markdown2

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['GET', 'POST'])
def query():
    if request.method == 'POST':
        user_query = request.form['user_query']
    else:
        user_query = request.args.get('user_query')

    response_text = fun(user_query, True)  # Call your 'fun' function with the user query

    if isinstance(response_text, list):
        # If the response is a list, assume it's a list of parts and concatenate them
        response_text = ''.join(response_text)

    response_markdown = markdown2.markdown(response_text)

    return render_template('result.html', response=response_markdown)

if __name__ == '__main__':
    app.run(debug=True)

