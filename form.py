from flask import Flask, render_template, request, jsonify
import requests
import google.generativeai as genai

app = Flask(__name__)

# Your API keys
MARKETSTACK_API_KEY = '80a2fee80e259f955e7558b713d5d138'
GEMINI_API_KEY = "AIzaSyAoHKRHtXA1MxxG1UFxyWEC6v8bzomMdww"

# Gemini setup
genai.configure(api_key=GEMINI_API_KEY)

# Get historical stock data from Marketstack
def get_marketstack_data(symbol):
    url = f'http://api.marketstack.com/v1/eod?access_key={MARKETSTACK_API_KEY}&symbols={symbol}&limit=10'
    response = requests.get(url)
    return response.json()

# Ask Gemini about the stock data
def resolve_query_with_gemini(user_query, stock_data):
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    Here's 10 days of historical EOD (end-of-day) stock data for {user_query.split()[0]}:
    {stock_data}

    Question: {user_query}

    Please analyze the trend and provide a meaningful answer based on this data.
    """

    response = model.generate_content(prompt)
    return {"response": response.text}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_data', methods=['POST'])
def get_data():
    symbol = request.form.get('symbol')
    data = get_marketstack_data(symbol)
    return jsonify(data)

@app.route('/query', methods=['POST'])
def query():
    symbol = request.form.get('symbol')
    question = request.form.get('query')
    stock_data = get_marketstack_data(symbol)
    resolution = resolve_query_with_gemini(question, stock_data)
    return jsonify(resolution)

if __name__ == '__main__':
    app.run(debug=True)
