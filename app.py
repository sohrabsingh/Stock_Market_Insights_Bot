from flask import Flask, render_template, request, jsonify
import requests
import google.generativeai as genai

# 🔐 Paste your API keys directly here
GEMINI_API_KEY = "AIzaSyAoHKRHtXA1MxxG1UFxyWEC6v8bzomMdww"
FINNHUB_API_KEY = "cvtpic9r01qjg135icbgcvtpic9r01qjg135icc0"

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    data = request.json
    symbol = data.get("symbol", "").upper()
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        quote = response.json()
        if 'c' not in quote or quote['c'] == 0:
            return jsonify({"error": "Invalid symbol or no data found."})
        return jsonify({
            "symbol": symbol,
            "current": quote["c"],
            "high": quote["h"],
            "low": quote["l"],
            "open": quote["o"],
            "previous_close": quote["pc"]
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get("message", "")
    
    # Custom handling for "highest priced stock" queries
    if "highest priced" in message or "most expensive stock" in message:
        symbols = ['AAPL', 'GOOGL', 'TSLA', 'MSFT', 'AMZN', 'BRK_A']
        highest = {"symbol": "", "price": 0}
        for sym in symbols:
            try:
                url = f"https://finnhub.io/api/v1/quote?symbol={sym}&token={FINNHUB_API_KEY}"
                res = requests.get(url)
                data = res.json()
                price = data.get("c", 0)
                if price and price > highest["price"]:
                    highest = {"symbol": sym, "price": price}
            except:
                continue
        if highest["symbol"]:
            return jsonify({"reply": f"The highest priced stock (from a sample list) is {highest['symbol']} at ${highest['price']:.2f}."})
        else:
            return jsonify({"reply": "Unable to fetch highest priced stock right now."})
    
    # Default Gemini response
    try:
        gemini_response = model.generate_content(message)
        return jsonify({"reply": gemini_response.text})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
