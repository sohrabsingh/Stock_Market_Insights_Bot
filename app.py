from flask import Flask, render_template, request, jsonify
import requests
import google.generativeai as genai

# 🔐 Paste your API keys directly here
GEMINI_API_KEY = "AIzaSyBmx0ZFgPQTf_ZaEP0DaWRG01Xn4itYRAY"
FINNHUB_API_KEY = "cvtsfb9r01qjg1362mv0cvtsfb9r01qjg1362mvg"

# Market configurations
MARKET_CONFIGS = {
    'IN': {
        'exchange': 'NSE',
        'currency': 'INR',
        'currency_symbol': '₹',
        'usd_to_local': 83.0  # USD to INR conversion rate
    },
    'US': {
        'exchange': 'US',
        'currency': 'USD',
        'currency_symbol': '$',
        'usd_to_local': 1.0
    },
    'UK': {
        'exchange': 'LSE',
        'currency': 'GBP',
        'currency_symbol': '£',
        'usd_to_local': 0.8  # USD to GBP conversion rate
    },
    'JP': {
        'exchange': 'TSE',
        'currency': 'JPY',
        'currency_symbol': '¥',
        'usd_to_local': 151.0  # USD to JPY conversion rate
    },
    'CN': {
        'exchange': 'SSE',
        'currency': 'CNY',
        'currency_symbol': '¥',
        'usd_to_local': 7.2  # USD to CNY conversion rate
    },
    'DE': {
        'exchange': 'FRA',
        'currency': 'EUR',
        'currency_symbol': '€',
        'usd_to_local': 0.92  # USD to EUR conversion rate
    }
}

# Company name to symbol mapping
COMPANY_MAP = {
    "apple": "AAPL",
    "nvidia": "NVDA",
    "microsoft": "MSFT",
    "google": "GOOGL",
    "amazon": "AMZN",
    "tesla": "TSLA",
    "meta": "META",
    "netflix": "NFLX",
    "intel": "INTC",
    "amd": "AMD",
    "ibm": "IBM",
    "oracle": "ORCL",
    "cisco": "CSCO",
    "adobe": "ADBE",
    "salesforce": "CRM"
}

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('newUI.html')

@app.route('/search_symbol', methods=['POST'])
def search_symbol():
    data = request.json
    query = data.get("query", "").strip()
    
    try:
        # Search for the symbol using Finnhub's search endpoint
        url = f"https://finnhub.io/api/v1/search?q={query}&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        results = response.json()
        
        if 'result' in results and results['result']:
            # Return the first matching result
            first_result = results['result'][0]
            return jsonify({
                "symbol": first_result['symbol'],
                "name": first_result['description'],
                "type": first_result['type']
            })
        else:
            return jsonify({"error": "No matching company found."})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    data = request.json
    symbol = data.get("symbol", "").upper()
    market = data.get("market", "IN")  # Default to Indian market
    
    if market not in MARKET_CONFIGS:
        return jsonify({"error": "Invalid market selected."})
    
    market_config = MARKET_CONFIGS[market]
    
    try:
        # First try to get the symbol if a company name was provided
        if not symbol.isalpha():
            search_url = f"https://finnhub.io/api/v1/search?q={symbol}&exchange={market_config['exchange']}&token={FINNHUB_API_KEY}"
            search_response = requests.get(search_url)
            search_results = search_response.json()
            
            if 'result' in search_results and search_results['result']:
                symbol = search_results['result'][0]['symbol']
            else:
                return jsonify({"error": f"Company not found in {market_config['exchange']} market. Try another name or symbol."})
        
        # Get the stock data
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        quote = response.json()
        
        if 'c' not in quote or quote['c'] == 0:
            return jsonify({"error": f"No stock data available for {symbol} in {market_config['exchange']} market."})
        
        # Convert prices to local currency
        def convert_price(price):
            return round(price * market_config['usd_to_local'], 2)
            
        return jsonify({
            "symbol": symbol,
            "current": convert_price(quote["c"]),
            "high": convert_price(quote["h"]),
            "low": convert_price(quote["l"]),
            "open": convert_price(quote["o"]),
            "previous_close": convert_price(quote["pc"]),
            "change": convert_price(quote["d"]),
            "percent_change": quote["dp"]
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
