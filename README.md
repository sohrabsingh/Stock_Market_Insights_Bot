Stock Market Insights Chatbot
Project Description
This project is a Stock Market Insights Chatbot built using Flask for the backend and Chart.js for displaying stock price trends. The chatbot integrates with the Finnhub API to provide real-time stock market data and historical price charts. The chatbot also handles stock-related queries and offers visual insights into the stock market.

Features
Real-time Stock Data: Fetch and display real-time stock data, including the current price, highest price, lowest price, and previous close.

Historical Stock Price Chart: Display a chart of stock prices over the last 5 days using data fetched from Finnhub.

Chatbot Integration: A simple chat interface to interact with the bot and ask questions related to stocks.

Prerequisites
Before running the app, ensure you have:

A Finnhub API key (you can get one from Finnhub)

Python (preferably 3.7 or higher) installed on your machine.

Setup and Installation
1. Clone the repository
First, clone the repository to your local machine:

bash
Copy
Edit
git clone <repository-url>
cd <repository-folder>
2. Install Dependencies
Create a requirements.txt file (if you haven't already) in the root folder, or you can install the dependencies directly using pip. To do this, create a virtual environment and install the required packages.

bash
Copy
Edit
python -m venv venv
source venv/bin/activate   # On Windows, use venv\Scripts\activate
pip install -r requirements.txt
3. Add Your API Key
In the app.py file, replace the FINNHUB_API_KEY placeholder with your actual API key.

python
Copy
Edit
FINNHUB_API_KEY = 'YOUR_FINNHUB_API_KEY'
4. Run the Application
Once the dependencies are installed and your API key is set up, you can run the Flask application.

bash
Copy
Edit
python app.py
By default, the Flask app will run at http://127.0.0.1:5000/.

5. Open the Application
Open your browser and navigate to http://127.0.0.1:5000/ to interact with the chatbot and view the stock market insights.

How It Works
The user inputs a stock ticker symbol (e.g., AAPL for Apple, TSLA for Tesla) into the chatbot.

The chatbot fetches real-time stock data (current price, high, low, previous close) from the Finnhub API.

It also fetches historical data (last 5 days) to plot a line chart of stock prices using Chart.js.

The user can ask more questions related to stocks, and the bot will respond accordingly.

Files Overview
app.py: Flask backend that handles API requests for stock data and chatbot responses.

index.html: Frontend HTML file containing the chatbot interface and stock chart.

requirements.txt: Lists all the required Python dependencies for the project.

Dependencies
Flask 2.x

requests 2.x

Chart.js (for frontend charting)

Troubleshooting
Issue with API Key: If you're getting an error related to the API key, ensure it's correctly placed in the app.py file.

API Limit Reached: Finnhub has rate limits. If you encounter this issue, you may need to wait for the rate limit to reset or upgrade your API key.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Note:
Replace <repository-url> and <repository-folder> with the actual URL and folder name of your project repository if you're hosting this on GitHub or another platform.

