from flask import Flask, render_template, request
from sec_edgar_downloader import Downloader
import os
import pandas as pd
import requests
import matplotlib.pyplot as plt
import re
import io
import base64

app = Flask(__name__)

# Function to download 10-K filings for a given company ticker
def download_10k_filings(ticker):
    dl = Downloader()
    directory = f'{ticker}_10k_filings'
    if not os.path.exists(directory):
        os.makedirs(directory)
    for year in range(1995, 2024):
        try:
            dl.get("10-K", ticker, year)
            print(f"Downloaded {ticker} 10-K filing for {year}")
        except Exception as e:
            print(f"Failed to download {ticker} 10-K filing for {year}: {e}")

# Function to merge and clean data
def merge_and_clean_data(ticker):
    directory = f'{ticker}_10k_filings'
    merged_data = pd.DataFrame()
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                filing_text = file.read()
                revenue_pattern = r"Total\s*Revenues?:?\s*\$?([\d,.]+)"
                earnings_pattern = r"Net\s*(?:Income|Earnings|Profit):?\s*\$?([\d,.]+)"
                year_pattern = r"For\s*the\s*Fiscal\s*Year\s*Ended\s*(\d{4})"
                revenue_match = re.search(revenue_pattern, filing_text, re.IGNORECASE)
                if revenue_match:
                    revenue = float(re.sub(r'[^\d.]+', '', revenue_match.group(1)))
                else:
                    revenue = None
                earnings_match = re.search(earnings_pattern, filing_text, re.IGNORECASE)
                if earnings_match:
                    earnings = float(re.sub(r'[^\d.]+', '', earnings_match.group(1)))
                else:
                    earnings = None
                year_match = re.search(year_pattern, filing_text, re.IGNORECASE)
                if year_match:
                    year = int(year_match.group(1))
                else:
                    year = None
                merged_data = merged_data.append({'Year': year, 'Revenue': revenue, 'Earnings': earnings}, ignore_index=True)
    merged_data['Revenue'] = merged_data['Revenue'].fillna(0)
    merged_data['Earnings'] = merged_data['Earnings'].fillna(0)
    merged_data['Year'] = merged_data['Year'].astype(int)
    return merged_data

# Function to generate insights on revenue growth and P/E ratio using OpenAI's LLM
def generate_insights(data):
    insights = {}
    for index, row in data.iterrows():
        text = row['text']  # Assuming 'text' is the column containing the text data
        company_name = row['company_name']  # Assuming 'company_name' is the column containing the company name
        prompt_revenue = f"Generate insights on revenue growth for {company_name} based on the following text:\n{text}"
        prompt_pe_ratio = f"Generate insights on price-to-earnings ratio for {company_name} based on the following text:\n{text}"
        revenue_growth_insight = generate_insight(prompt_revenue)
        pe_ratio_insight = generate_insight(prompt_pe_ratio)
        insights[f'Revenue Growth_{index}'] = revenue_growth_insight
        insights[f'Price-to-Earnings Ratio_{index}'] = pe_ratio_insight
    return insights

# Function to call OpenAI's LLM API and generate insight for a given prompt
def generate_insight(prompt):
    api_key = 'YOUR_API_KEY'
    url = 'https://api.openai.com/v1/engines/davinci-codex/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        'prompt': prompt,
        'max_tokens': 200,
        'temperature': 0.5,
        'top_p': 1.0,
        'frequency_penalty': 0.0,
        'presence_penalty': 0.0
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        insight = response.json()['choices'][0]['text'].strip()
        return insight
    else:
        print(f"Error: {response.status_code}")
        return None

# Route for the homepage
@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Company 10-K Analysis</title>
    </head>
    <body>
        <h1>Company 10-K Analysis</h1>
        <p>Enter a company ticker to analyze:</p>
        <form action="/analyze" method="POST">
            <input type="text" name="ticker" placeholder="Company Ticker" required>
            <button type="submit">Analyze</button>
        </form>
    </body>
    </html>
    """

# Route to handle form submission
@app.route('/analyze', methods=['POST'])
def analyze():
    ticker = request.form['ticker']
    download_10k_filings(ticker)
    merged_data = merge_and_clean_data(ticker)
    insights = generate_insights(merged_data)
    plot = visualize_insights(insights)  # Generate Matplotlib plot
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Visualization</title>
    </head>
    <body>
        <h1>Insights Visualization</h1>
        <div>{plot}</div>
    </body>
    </html>
    """

# Function to visualize insights using Matplotlib
def visualize_insights(insights):
    plt.figure(figsize=(10, 6))
    plt.plot(years, revenue_growth, label='Revenue Growth')
    plt.plot(years, pe_ratio, label='Price-to-Earnings Ratio')
    plt.xlabel('Year')
    plt.ylabel('Value')
    plt.title('Insights on Revenue Growth and Price-to-Earnings Ratio')
    plt.legend()
    plt.grid(True)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    return f'<img src="data:image/png;base64,{plot_data}">'

if __name__ == '__main__':
    app.run(debug=True)