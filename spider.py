import requests as r
from bs4 import BeautifulSoup
from urllib.parse import *
import collections
# import time
import os


class BasicCrawler:
    
    def __init__(self, start_url, output_file='url_output.txt', user_agent=None, max_depth = 1):
        self.start_url = start_url
        self.output_file = output_file
        self._max_depth = max_depth
        
        self._crawl_queue = collections.deque([(start_url, 0)])
        self.total_visited_urls = {start_url}
        self.all_extracted_urls = set()
        self.base_netloc = urlparse(start_url).netloc
        
        self.session = r.Session()
        self.headers =  {'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        self.session.headers.update(self.headers)
    
    
    def _fetch_page(self, url):
        try:
            # time.sleep(0.5)
            req_made = self.session.get(url, timeout=5)
            req_made.raise_for_status()
            return req_made.text
        except r.exceptions.RequestException as e:
            print(f"Error fetching the url {e}")
            return None
    
    
    def _create_absolute_links(self, html_content, current_url, current_depth):
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for link in soup.find_all('a'):
            href = link.get('href')
            
            if href and not href.startswith('#') and href.strip():
                absolute_url = urljoin(current_url, href)
                
                self.all_extracted_urls.add(absolute_url)
                link_netloc = urlparse(absolute_url).netloc
                
                if (link_netloc == self.base_netloc and absolute_url not in self.total_visited_urls and current_depth < self._max_depth):
                    self.total_visited_urls.add(absolute_url)
                    self._crawl_queue.append((absolute_url, current_depth + 1))                    
    
    
    def _write_to_file(self):
        try:
            with open(self.output_file, 'w', encoding='utf-8') as file:
                for link in sorted(list(self.all_extracted_urls)):
                    file.write(link+'\n')
                    
        except Exception as e:
            print(f'An exception occurred: {e}')
    
    
    def run(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
        
        self.total_visited_urls.add(self.start_url)
        
        while self._crawl_queue:
            current_url, current_depth = self._crawl_queue.popleft()
            
            html = self._fetch_page(current_url)
            
            if html:
                self._create_absolute_links(html, current_url, current_depth)

        self._write_to_file()



# execution zone 
site_to_crawl = 'https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/'

my_crawler = BasicCrawler(start_url=site_to_crawl, output_file='owasp_links.txt', max_depth=2)
my_crawler.run()