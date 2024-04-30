import os
import requests
import urllib3
from googlesearch import search
from bs4 import BeautifulSoup
import json

# Disable SSL certificate verification
http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)

def fetch_livestreams(api_key, query):
    url = f'https://www.googleapis.com/youtube/v3/search?key={api_key}&part=snippet&type=video&eventType=live&q={query}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        livestreams = response.json().get('items', [])
        return livestreams
    except requests.RequestException as e:
        print(f'Failed to fetch livestreams: {e}')
        return []

def extract_keywords_from_page(url):
    try:
        response = http.request('GET', url)
        if response.status == 200:
            soup = BeautifulSoup(response.data, 'html.parser')
            text = soup.get_text()
            words = text.split()
            word_freq = {}
            for word in words:
                word = word.lower()
                if word.isalpha():
                    word_freq[word] = word_freq.get(word, 0) + 1
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            top_keywords = [word[0] for word in sorted_words[:10]]
            return top_keywords
        else:
            print(f'Error fetching page: HTTP {response.status}')
            return []
    except Exception as e:
        print(f'Error extracting keywords from page: {e}')
        return []

def generate_keyword_ideas(query):
    keyword_ideas = []
    try:
        for result in search(query, num=5, stop=5, pause=2):
            keywords = extract_keywords_from_page(result)
            keyword_ideas.append({'url': result, 'keywords': keywords})
    except Exception as e:
        print(f'Error generating keyword ideas: {e}')
    return keyword_ideas

def lambda_handler(event, context):
    query = event['query']
    API_KEY = os.getenv('API_KEY', 'AIzaSyAVZhXNtFnRkq0Dzx8WZLTd4hxRo-w98q4')
    
    livestreams = fetch_livestreams(API_KEY, query)
    keyword_ideas = generate_keyword_ideas(query)
    
    response = {
        'statusCode': 200,
        'body': json.dumps({
            'livestreams': livestreams,
            'keyword_ideas': keyword_ideas
        })
    }
    
    return response

if __name__ == '__main__':
    event = {'query': 'zindagi'}  # Replace 'zindagi' with your desired query
    context = {}
    
    result = lambda_handler(event, context)
    print("Lambda Handler Result:")
    print(json.dumps(result, indent=4))