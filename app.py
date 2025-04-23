from flask import Flask, render_template, request, jsonify
import requests
import google.generativeai as genai
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# 🔐 Paste your API keys directly here
GEMINI_API_KEY = "AIzaSyBmx0ZFgPQTf_ZaEP0DaWRG01Xn4itYRAY"
FINNHUB_API_KEY = "cvtsfb9r01qjg1362mv0cvtsfb9r01qjg1362mvg"
ALPHA_VANTAGE_API_KEY = "HHB2E7F9CS4GTSR1"  # Get from www.alphavantage.co

# Market configurations
MARKET_CONFIGS = {
    'IN': {
        'exchange': 'NSE',
        'currency': 'INR',
        'currency_symbol': '₹',
        'usd_to_local': 86.0  # USD to INR conversion rate
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

def search_company(query, market='US'):
    """Search for company using fuzzy matching and Alpha Vantage API"""
    # First try fuzzy matching with our existing database
    query = query.lower().strip()
    # Direct match check first
    if query in COMPANY_MAP:
        return [(COMPANY_MAP[query], query)]
    
    # Then try fuzzy matching with a lower score threshold
    matches = process.extractBests(query, COMPANY_MAP.keys(), score_cutoff=60, limit=5)
    if matches:
        return [(COMPANY_MAP[name], name) for name, score in matches]
    
    # If no good matches, search using Alpha Vantage API
    try:
        url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={query}&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        if 'bestMatches' in data:
            results = []
            for match in data['bestMatches']:
                symbol = match['1. symbol']
                name = match['2. name']
                region = match['4. region']
                
                # Filter by market if specified
                if market == 'US' and not any(x in region for x in ['United States', 'NYSE', 'NASDAQ']):
                    continue
                elif market == 'IN' and 'India' not in region:
                    continue
                # Add more market filters as needed
                
                results.append((symbol, name))
            return results[:5]
    except Exception as e:
        print(f"Alpha Vantage API error: {e}")
    
    return []

# Company name to symbol mapping
COMPANY_MAP = {
    # US Companies
    "apple": "AAPL", "apple inc": "AAPL",
    "nvidia": "NVDA", "nvidia corporation": "NVDA",
    "microsoft": "MSFT", "microsoft corporation": "MSFT",
    "google": "GOOGL", "alphabet": "GOOGL", "alphabet inc": "GOOGL",
    "amazon": "AMZN", "amazon.com": "AMZN",
    "tesla": "TSLA", "tesla inc": "TSLA",
    "meta": "META", "facebook": "META", "meta platforms": "META",
    "netflix": "NFLX", "netflix inc": "NFLX",
    "intel": "INTC", "intel corporation": "INTC",
    "amd": "AMD", "advanced micro devices": "AMD",
    "ibm": "IBM", "international business machines": "IBM",
    "oracle": "ORCL", "oracle corporation": "ORCL",
    "cisco": "CSCO", "cisco systems": "CSCO",
    "adobe": "ADBE", "adobe inc": "ADBE",
    "salesforce": "CRM", "salesforce.com": "CRM",
    
    # Indian Companies
    "reliance": "RELIANCE.NS", "reliance industries": "RELIANCE.NS",
    "tcs": "TCS.NS", "tata consultancy services": "TCS.NS",
    "infosys": "INFY.NS", "infosys limited": "INFY.NS",
    "hdfc": "HDFC.NS", "hdfc bank": "HDFCBANK.NS",
    "wipro": "WIPRO.NS", "wipro limited": "WIPRO.NS",
    "bharti airtel": "BHARTIARTL.NS", "airtel": "BHARTIARTL.NS",
    "itc": "ITC.NS", "itc limited": "ITC.NS",
    
    # UK Companies
    "hsbc": "HSBA.L", "hsbc holdings": "HSBA.L",
    "bp": "BP.L", "british petroleum": "BP.L",
    "vodafone": "VOD.L", "vodafone group": "VOD.L",
    "barclays": "BARC.L", "barclays plc": "BARC.L",
    
    # Japanese Companies
    "toyota": "7203.T", "toyota motor": "7203.T",
    "sony": "6758.T", "sony group": "6758.T",
    "honda": "7267.T", "honda motor": "7267.T",
    "nintendo": "7974.T", "nintendo co": "7974.T",
    
    # Chinese Companies
    "alibaba": "9988.HK", "alibaba group": "9988.HK",
    "tencent": "0700.HK", "tencent holdings": "0700.HK",
    "baidu": "9888.HK", "baidu inc": "9888.HK",
    "jd": "9618.HK", "jd.com": "9618.HK",
    
    # German Companies
    "volkswagen": "VOW3.DE", "vw": "VOW3.DE",
    "siemens": "SIE.DE", "siemens ag": "SIE.DE",
    "bmw": "BMW.DE", "bayerische motoren werke": "BMW.DE",
    "sap": "SAP.DE", "sap se": "SAP.DE"
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
    query = data.get("query", "").strip().lower()
    
    try:
        # First check if the query matches any known company names
        for company_name, symbol in COMPANY_MAP.items():
            if query in company_name.lower() or company_name.lower() in query:
                return jsonify({
                    "symbol": symbol,
                    "name": company_name.title(),
                    "type": "Common Stock"
                })
        
        # If no direct match found, try Finnhub's search endpoint
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
    query = data.get("symbol", "").strip()
    market = data.get("market", "IN")
    
    if market not in MARKET_CONFIGS:
        return jsonify({"error": "Invalid market selected."})
    
    market_config = MARKET_CONFIGS[market]
    
    try:
        # First try fuzzy search in our database
        matches = search_company(query, market)
        if matches:
            symbol = matches[0][0]  # Use the best match
            suggestions = [{'symbol': sym, 'name': name} for sym, name in matches[1:]] if len(matches) > 1 else []
        else:
            # Try Alpha Vantage search as backup
            url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={query}&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()
            
            if 'bestMatches' in data and data['bestMatches']:
                match = data['bestMatches'][0]
                symbol = match['1. symbol']
                suggestions = [{
                    'symbol': m['1. symbol'],
                    'name': m['2. name']
                } for m in data['bestMatches'][1:4]]
            else:
                return jsonify({"error": "Company not found. Please try another name or symbol."})
        
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
