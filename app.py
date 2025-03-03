import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse

# Function to scrape the sitemap
def scrape_sitemap(url):
    # Check if the URL has a scheme (http or https)
    if not urlparse(url).scheme:
        url = 'https://' + url

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')  # Use lxml for parsing
    urls = [element.text for element in soup.find_all('loc')]
    return urls

# Function to get PageSpeed Insights
def get_pagespeed_insights(url, api_key):
    response = requests.get(f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
                            params={"url": url, "key": api_key})
    data = response.json()

    # Initialize a dictionary to store the extracted data
    insights = {}

    # Basic info
    insights['URL'] = url
    insights['Overall Score'] = data.get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score')

    # Audits data
    audits = data.get('lighthouseResult', {}).get('audits')

    # Extracting specific metrics
    insights['First Contentful Paint'] = audits.get('first-contentful-paint', {}).get('displayValue')
    insights['Speed Index'] = audits.get('speed-index', {}).get('displayValue')
    insights['Largest Contentful Paint'] = audits.get('largest-contentful-paint', {}).get('displayValue')
    insights['Time to Interactive'] = audits.get('interactive', {}).get('displayValue')
    insights['Total Blocking Time'] = audits.get('total-blocking-time', {}).get('displayValue')
    insights['Cumulative Layout Shift'] = audits.get('cumulative-layout-shift', {}).get('displayValue')

    # You can add more fields as needed

    return insights

# Streamlit app
def main():
    st.title("Sitemap Scraper and PageSpeed Insights")
    input_url = st.text_input("Enter the URL of the sitemap (e.g., https://example.com/sitemap.xml):")

    # Retrieve the API key from Streamlit secrets
    api_key = st.secrets["pagespeed_api_key"]

    if st.button("Scrape and Analyze"):
        if input_url:
            scraped_urls = scrape_sitemap(input_url)
            total_urls = len(scraped_urls)
            results = []

            # Initialize a progress bar
            progress_bar = st.progress(0)
            progress_text = st.empty()

            # Create a placeholder for the table
            table_placeholder = st.empty()

            for index, url in enumerate(scraped_urls, start=1):
                insights = get_pagespeed_insights(url, api_key)
                results.append(insights)
                progress_bar.progress(index / total_urls)
                progress_text.text(f"Processing URL {index} of {total_urls}")

                # Update the table in the placeholder
                df = pd.DataFrame(results)
                table_placeholder.write(df)

            # Final update to progress bar and text
            progress_bar.empty()
            progress_text.empty()

            # Download link for DataFrame
            st.download_button(label="Download data as CSV",
                               data=df.to_csv().encode('utf-8'),
                               file_name='pagespeed_insights.csv',
                               mime='text/csv')

if __name__ == "__main__":
    main()
