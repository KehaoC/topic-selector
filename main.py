from scholarly import scholarly
from paper import Paper
from mockdata import *
from crawlers import *
import os

# Configuration Parameters
KEYWORDS = keywords  # 记录在 mockdata 中了
OUTPUT_DIR = f"output/{time.strftime('%Y-%m-%d_%H-%M-%S')}"
GOOGLE_SCHOLAR_CONFIG = {
    "max_citation_count": 10,
    "max_results": 10,
    "max_years": 5
}

def main():
    print("Welcome to the topic selector!")

    
    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for keyword in KEYWORDS:
        with open(f"{OUTPUT_DIR}/{keyword}.txt", "w", encoding="utf-8") as f:
            f.write("Parameters:\n")
            f.write(f"Working on Keyword: {keyword}\n")
            f.write(f"Max Citation Count: {GOOGLE_SCHOLAR_CONFIG['max_citation_count']}\n")
            f.write(f"Max Results: {GOOGLE_SCHOLAR_CONFIG['max_results']}\n")
            f.write(f"Max Years: {GOOGLE_SCHOLAR_CONFIG['max_years']}\n\n")
        print(f"Processing on keyword: {keyword}...")
        papers: list[Paper] = GoogleScholarCrawler(
            keyword, 
            max_citation_count=GOOGLE_SCHOLAR_CONFIG["max_citation_count"],
            max_results=GOOGLE_SCHOLAR_CONFIG["max_results"],
            max_years=GOOGLE_SCHOLAR_CONFIG["max_years"]
        ).crawl()

        # Update file path to use OUTPUT_DIR
        output_file = os.path.join(OUTPUT_DIR, f"{keyword}.txt")
        
        # 2. 对论文进行关键词分解，分解成 keywordsList
        for paper in papers:
            paper.keywords = paper.keyword_decomposition()
        
        # 3. 对爬取到的论文的关键字进行知网爬虫
        # Write to text file
        with open(f"{OUTPUT_DIR}/{keyword}.txt", "a", encoding="utf-8") as f:
            for paper in papers:
                paper.related_chinese_papers = ZhiWangCrawler(paper.keywords).crawl()

                f.write("\n" + "=" * 80 + "\n")
                f.write(f"📄 Title: {paper.title}\n")
                f.write(f"🚩 Abstract: {paper.abstract}\n")
                f.write(f"🔑 Keywords: {', '.join(paper.keywords)}\n")
                f.write(f"🔗 URL: {paper.url}\n")
                f.write(f"📊 Citations: {paper.citation_count}\n")
                f.write("\n")
                f.write("Related Chinese Papers Numbers:\n")
                f.write(f"{len(paper.related_chinese_papers)}\n")
                f.write("-" * 80 + "\n")
                for i, related_paper in enumerate(paper.related_chinese_papers, 1):
                    f.write(f"{i}. {related_paper.title}\n")
                    f.write(f"   🚩 Abstract: {related_paper.abstract}\n")
                    f.write(f"   🔗 URL: {related_paper.url}\n")
                    f.write(f"   📊 Citations: {related_paper.citation_count}\n")
                    f.write("\n")
                f.write("=" * 80 + "\n\n")

def test_google_scholar_crawler():
    print("test_google_scholar_crawler")
    mockkeyword = KEYWORDS[0]
    papers = GoogleScholarCrawler(
        mockkeyword,
        max_citation_count=GOOGLE_SCHOLAR_CONFIG["max_citation_count"],
        max_results=3,
        max_years=GOOGLE_SCHOLAR_CONFIG["max_years"]
    ).crawl()
    for paper in papers:
        print(paper.print_info())

def test_keyword_decomposition():
    paper = papers_data[1]
    paper.keyword_decomposition()
    print(paper.print_info())

def test_zhiwang_crawler():
    paper = papers_data[1]
    paper.keywords = ['长期激励', '短期激励', '企业创新']
    related_chinese_papers = ZhiWangCrawler(paper.keywords).crawl()
    for paper in related_chinese_papers:
        print(paper.print_info())

if __name__ == "__main__":
    # test_google_scholar_crawler()
    # test_keyword_decomposition()
    # test_zhiwang_crawler()
    main()