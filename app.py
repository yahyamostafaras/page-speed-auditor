import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse

# Function to scrape the sitemap
def scrape_sitemap(url):
    # Ensure the URL has a scheme (http or https)
    if not urlparse(url).scheme:
        url = 'https://' + url

    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Failed to fetch sitemap: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.content, 'lxml')  # Use lxml for XML parsing
    urls = [element.text for element in soup.find_all('loc')]
    
    if not urls:
        st.warning("No URLs found in the sitemap.")
    
    return urls

# Function to get PageSpeed Insights
def get_pagespeed_insights(url, api_key):
    response = requests.get(
        "https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
        params={"url": url, "key": api_key}
    )
    
    data = response.json()

    # Handle missing data gracefully
    if 'lighthouseResult' not in data:
        st.warning(f"Skipping {url}: No Lighthouse results found.")
        return {"URL": url, "Overall Score": "N/A"}

    insights = {"URL": url}
    categories = data.get('lighthouseResult', {}).get('categories', {})
    audits = data.get('lighthouseResult', {}).get('audits', {})

    insights['Overall Score'] = categories.get('performance', {}).get('score', 'N/A')
    insights['First Contentful Paint'] = audits.get('first-contentful-paint', {}).get('displayValue', 'N/A')
    insights['Speed Index'] = audits.get('speed-index', {}).get('displayValue', 'N/A')
    insights['Largest Contentful Paint'] = audits.get('largest-contentful-paint', {}).get('displayValue', 'N/A')
    insights['Time to Interactive'] = audits.get('interactive', {}).get('displayValue', 'N/A')
    insights['Total Blocking Time'] = audits.get('total-blocking-time', {}).get('displayValue', 'N/A')
    insights['Cumulative Layout Shift'] = audits.get('cumulative-layout-shift', {}).get('displayValue', 'N/A')

    return insights

# Streamlit app
def main():
    st.title("Sitemap Scraper and PageSpeed Insights")

    input_url = st.text_input("Enter the URL of the sitemap (e.g., https://example.com/sitemap.xml):")

    # Retrieve the API key from Streamlit secrets
    try:
        api_key = st.secrets["pagespeed_api_key"]
    except KeyError:
        st.error("API Key not found. Please ensure it's set in `secrets.toml`.")
        return

    if st.button("Scrape and Analyze"):
        if input_url:
            scraped_urls = scrape_sitemap(input_url)
            total_urls = len(scraped_urls)

            if total_urls == 0:
                st.error("No valid URLs found in the sitemap.")
                return

            results = []

            # Initialize a progress bar and placeholder for dynamic table
            progress_bar = st.progress(0)
            progress_text = st.empty()
            table_placeholder = st.empty()

            for index, url in enumerate(scraped_urls, start=1):
                insights = get_pagespeed_insights(url, api_key)
                results.append(insights)
                
                # Update progress bar
                progress_bar.progress(index / total_urls)
                progress_text.text(f"Processing URL {index} of {total_urls}")

                # Dynamically update the table
                df = pd.DataFrame(results)
                table_placeholder.write(df)

            # Final update to progress bar and text
            progress_bar.empty()
            progress_text.empty()

            # Provide a download button for results
            st.download_button(
                label="Download data as CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name='pagespeed_insights.csv',
                mime='text/csv'
            )

if __name__ == "__main__":
    main()
