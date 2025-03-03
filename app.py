import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to scrape the sitemap
def scrape_sitemap(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    urls = [element.text for element in soup.find_all('loc')]
    return urls

# Function to get PageSpeed Insights
def get_pagespeed_insights(url, api_key):
    # Example API request:
    # https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={api_key}
    response = requests.get(f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
                            params={"url": url, "key": api_key})
    return response.json()

# Streamlit app
def main():
    st.title("Sitemap Scraper and PageSpeed Insights")
    input_url = st.text_input("Enter the URL of the sitemap (e.g., https://example.com/sitemap.xml):")
    api_key = st.text_input("Enter your Google PageSpeed Insights API Key:")
    
    if st.button("Scrape and Analyze"):
        if input_url and api_key:
            scraped_urls = scrape_sitemap(input_url)
            results = []
            for url in scraped_urls:
                insights = get_pagespeed_insights(url, api_key)
                # Process the insights data as needed
                results.append({"URL": url, "Insights": insights})
            
            df = pd.DataFrame(results)
            st.write(df)

            # Download link for DataFrame
            st.download_button(label="Download data as CSV",
                               data=df.to_csv().encode('utf-8'),
                               file_name='pagespeed_insights.csv',
                               mime='text/csv')

if __name__ == "__main__":
    main()

