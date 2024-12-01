from paper import Paper
from scholarly import scholarly
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import Options as ChromeOptions
import time
import requests
from paper import Paper
from webdriver_manager.chrome import ChromeDriverManager
import platform

class GoogleScholarCrawler:
    def __init__(self, keyword, max_citation_count=10, max_results=10, max_years = 5):
        self.keyword = keyword
        self.max_citation_count = max_citation_count
        self.max_results = max_results
        self.max_years = max_years
        
    def crawl(self):
        try:
            print(f"Starting Google Scholar search for keyword: {self.keyword}")
            print("Searching publications...")
            
            search_query = scholarly.search_pubs(self.keyword)
            papers = []
            count = 0
            
            for result in search_query:
                if count >= self.max_results:
                    break
                
                try:
                    # Get citation count from the num_citations field
                    citation_count = result.get('num_citations', 0)
                    title = result.get('bib', {}).get('title', '')
                    url = result.get('pub_url', '')
                    abstract = result.get('bib', {}).get('abstract', '')
                    
                    # Only collect papers with citations below threshold
                    if citation_count <= self.max_citation_count:
                        print(f"Found paper {count + 1}: {title} (citations: {citation_count})")
                        paper = Paper(title, url, abstract, citation_count)
                        papers.append(paper)
                        count += 1
                        
                except AttributeError as e:
                    print(f"Skipping a result due to missing data: {str(e)}")
                    continue
            
            print(f"Successfully found {len(papers)} papers")
            return papers
            
        except Exception as e:
            print(f"Error crawling Google Scholar: {str(e)}")
            return []


class ZhiWangCrawler:
    def __init__(self, keywords, max_results=10):
        self.keywords = keywords
        self.max_results = max_results
        self.driver = None
        
    def _setup_driver(self):
        # print("Setting up Chrome driver...")
        option = ChromeOptions()
        option.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # macOS 特定配置
        if platform.system() == 'Darwin':  # Darwin 是 macOS 的系统名
            option.add_argument('--disable-gpu')
            option.add_argument('--no-sandbox')
            option.add_argument('--disable-dev-shm-usage')
            
            # 如果是 M1/M2 芯片，添加以下配置
            if platform.processor() == 'arm':
                option.add_argument('--disable-software-rasterizer')
        
        # 通用配置
        option.add_argument('blink-settings=imagesEnabled=false')
        option.add_argument("--headless")  # 无头模式
        
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        option.add_argument(f'user-agent={user_agent}')
        
        # 使用 webdriver_manager 自动管理 ChromeDriver
        service = Service(ChromeDriverManager().install())
        # print("Chrome driver setup complete")
        return webdriver.Chrome(options=option, service=service)
    def crawl(self):
        try:
            keyword = " ".join(self.keywords)
            print(f"Starting Zhi Wang search for keyword: {keyword}")
            print("Setting up web driver...")
            
            base_url = "https://kns.cnki.net/kns8s/defaultresult/index"
            url = f"{base_url}?crossids=YSTT4HG0&korder=SU&kw={keyword}"
            
            self.driver = self._setup_driver()
            print("Web driver setup complete")
            print(f"Navigating to URL: {url}")
            self.driver.get(url)
            
            papers = []
            count = 0
            
            while count < self.max_results:
                print("Waiting for page to load...")
                time.sleep(3)  # Wait for page load
                print("Finding paper elements on current page...")
                paper_elements = self.driver.find_elements(By.XPATH, '//div[@id="gridTable"]//table[@class="result-table-list"]/tbody/tr')
                print(f"Found {len(paper_elements)} paper elements")
                
                for element in paper_elements:
                    if count >= self.max_results:
                        break
                        
                    try:
                        print("Extracting paper details...")
                        title = element.find_element(By.CSS_SELECTOR, 'td.name a').text
                        print(f"Found Paper Title: {title}")
                        url = element.find_element(By.CSS_SELECTOR, 'td.name a').get_attribute("href")
                        citation_count = element.find_element(By.CSS_SELECTOR, 'td.quote').text
                        citation_count = int(citation_count) if citation_count else 0
                        
                        # print(f"Getting abstract for paper: {title}")
                        abstract = self._get_paper_abstract(url)
                        
                        paper = Paper(title, url, abstract, citation_count)
                        papers.append(paper)
                        count += 1
                        # print(f"Found paper {count}: {title} (citations: {citation_count})")
                        # print(f"Abstract length: {len(abstract)} characters")
                        
                    except Exception as e:
                        print(f"Error processing paper: {str(e)}")
                        continue
                
                try:
                    print("Looking for next page button...")
                    next_button = self.driver.find_element(By.XPATH, '//*[@id="PageNext"]')
                    print("Clicking next page...")
                    next_button.click()
                except:
                    print("No more pages available")
                    break
            
            print(f"Successfully found {len(papers)} papers")
            return papers
            
        except Exception as e:
            print(f"Error crawling Zhi Wang: {str(e)}")
            return []
            
        finally:
            if self.driver:
                print("Closing web driver...")
                self.driver.quit()
                print("Web driver closed")


    def _get_paper_abstract(self, paper_url):
        try:
            print(f"Getting abstract for paper: {paper_url}")
            detail_driver = self._setup_driver()
            detail_driver.get(paper_url)
            time.sleep(2)
            
            abstract = ""
            infos = detail_driver.find_elements(By.CSS_SELECTOR, 'div.doc-top div.row')
            for info in infos:
                text = info.text.strip()
                if "摘要：" in text:
                    abstract = text.replace("摘要：", "").strip()
                    break
                    
            return abstract
            
        except Exception as e:
            print(f"Error getting abstract: {str(e)}")
            return ""
            
        finally:
            if detail_driver:
                detail_driver.quit()