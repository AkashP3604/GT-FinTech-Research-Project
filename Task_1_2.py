import requests
import os
import pandas as pd
import matplotlib.pyplot as plt
import re

# Function to download and merge data
def merge_and_clean_data(ticker):
    # Directory containing the downloaded filings
    directory = f'{ticker}_10k_filings'
    merged_data = pd.DataFrame()

    # Loop through each downloaded filing
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                filing_text = file.read()

                # Regular expressions to extract relevant information
                revenue_pattern = r"Total\s*Revenues?:?\s*\$?([\d,.]+)"
                earnings_pattern = r"Net\s*(?:Income|Earnings|Profit):?\s*\$?([\d,.]+)"
                year_pattern = r"For\s*the\s*Fiscal\s*Year\s*Ended\s*(\d{4})"

                # Extract revenue
                revenue_match = re.search(revenue_pattern, filing_text, re.IGNORECASE)
                if revenue_match:
                    revenue = float(re.sub(r'[^\d.]+', '', revenue_match.group(1)))
                else:
                    revenue = None

                # Extract earnings
                earnings_match = re.search(earnings_pattern, filing_text, re.IGNORECASE)
                if earnings_match:
                    earnings = float(re.sub(r'[^\d.]+', '', earnings_match.group(1)))
                else:
                    earnings = None

                # Extract year
                year_match = re.search(year_pattern, filing_text, re.IGNORECASE)
                if year_match:
                    year = int(year_match.group(1))
                else:
                    year = None

                # Append extracted data to the merged_data dataframe
                merged_data = merged_data.append({'Year': year, 'Revenue': revenue, 'Earnings': earnings}, ignore_index=True)

    # Clean the merged data
    merged_data['Revenue'] = merged_data['Revenue'].fillna(0)  # Fill missing revenue values with 0
    merged_data['Earnings'] = merged_data['Earnings'].fillna(0)  # Fill missing earnings values with 0
    merged_data['Year'] = merged_data['Year'].astype(int)  # Convert 'Year' column to integer type

    return merged_data

# Function to generate insights on revenue growth and P/E ratio using OpenAI's LLM
def generate_insights(data):
    insights = {}

    # Placeholder logic to analyze text and generate insights using OpenAI's LLM
    for index, row in data.iterrows():
        text = row['text']
        company_name = row['company_name']
        
        # Call OpenAI's LLM API to generate insights on revenue growth
        prompt = f"Generate insights on revenue growth for {company_name} based on the following text:\n{text}"
        revenue_growth_insight = generate_insight(prompt)

        # Call OpenAI's LLM API to generate insights on price-to-earnings ratio
        prompt = f"Generate insights on price-to-earnings ratio for {company_name} based on the following text:\n{text}"
        pe_ratio_insight = generate_insight(prompt)

        insights[f'Revenue Growth_{index}'] = revenue_growth_insight
        insights[f'Price-to-Earnings Ratio_{index}'] = pe_ratio_insight

    return insights

# Function to call OpenAI's LLM API and generate insight for a given prompt
def generate_insight(prompt):
    api_key = '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'
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

# Function to visualize insights
def visualize_insights(insights):
    # Create a line plot to visualize revenue growth and P/E ratio over time
    years = range(1995, 2024)
    revenue_growth = [insights.get('Revenue Growth', '')] * len(years)
    pe_ratio = [insights.get('Price-to-Earnings Ratio', '')] * len(years)

    plt.figure(figsize=(10, 6))
    plt.plot(years, revenue_growth, label='Revenue Growth')
    plt.plot(years, pe_ratio, label='Price-to-Earnings Ratio')
    plt.xlabel('Year')
    plt.ylabel('Value')
    plt.title('Insights on Revenue Growth and Price-to-Earnings Ratio')
    plt.legend()
    plt.grid(True)
    plt.show()

# Usage for three company tickers
tickers = ['AAPL', 'NVDA', 'TSLA']

for ticker in tickers:
    merged_data = merge_and_clean_data(ticker)
    insights = generate_insights(merged_data)
    visualize_insights(insights)