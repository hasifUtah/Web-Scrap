from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

def fetch_articles():
    base_url = "https://sea.mashable.com/"
    page_url = base_url
    articles = []

    while page_url:
        response = requests.get(page_url)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Failed to retrieve page: {page_url}, status code: {response.status_code}")
            break
        
        soup = BeautifulSoup(response.content, 'html.parser')
        print(f"Fetching page: {page_url}")
        
        # Find articles on the current page
        for item in soup.find_all('li', class_='blogroll'):
            title_element = item.find('a')
            if title_element:
                title = title_element.get_text(strip=True)
                link = title_element['href']
                
                # If the link is relative, prepend the base URL
                if link.startswith('/'):
                    link = base_url + link

                # Attempt to find the publication date
                date_element = item.find('time')
                if date_element:
                    date_text = date_element.get_text(strip=True)
                    try:
                        date = datetime.strptime(date_text, '%B %d, %Y')
                    except ValueError:
                        date = datetime.now()  # Fallback if date parsing fails
                else:
                    date = datetime.now()  # Fallback if no date found
                
                # Only keep articles from January 1, 2022 onwards
                if date >= datetime(2022, 1, 1):
                    articles.append((title, link, date))
        
        # Find the next page URL
        next_page = soup.find('a', class_='next')  # Update this class name as needed
        if next_page and 'href' in next_page.attrs:
            page_url = base_url + next_page['href']
        else:
            page_url = None  # No more pages
    
    print("Fetched Articles:", articles)
    articles.sort(key=lambda x: x[2], reverse=True)
    print("Processed Articles:", articles)

    return articles

@app.route('/')
def index():
    articles = fetch_articles()
    print("Articles to be rendered:", articles)
    return render_template('index.html', articles=articles)

if __name__ == '__main__':
    app.run(debug=True)
