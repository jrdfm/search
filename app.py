#!/usr/bin/python3
# app.py
from flask import Flask, render_template, request, Markup
# from test import fun  # Import your implementation of the 'fun' function
from test import fun

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    user_query = request.form['user_query']
    response_text = fun(user_query)  # Call your 'fun' function with the user query
    response_markdown = Markup(response_text)  # Mark the response as safe HTML (to render Markdown)

    return render_template('result.html', response=response_markdown)

if __name__ == '__main__':
    app.run(debug=True)
