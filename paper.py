from groq import Groq
import json
from dotenv import load_dotenv
import os

load_dotenv()

prompt = """
You are an academic assistant specializing in extracting core keywords from research papers. I will provide the title and abstract of a paper, and your task is to identify the two or three most critical keywords. The extracted keywords should be output in a JSON format and translated into Chinese using precise and formal academic terminology, suitable for searching related papers in China National Knowledge Infrastructure (CNKI).

The JSON structure is as follows:
{{
  "keywords": [
    // The two or three most critical keywords translated into Chinese
  ]
}}

Requirements:
	1.	Extract the most essential concepts or topics from the given title and abstract.
	2.	Use accurate and standard academic terms in Chinese for the translation.
	3.	The output should only contain the most critical keywords, no more than three, avoiding redundancy.
    4.	No additional information is required, only the JSON output in the specified format.
	5.	The domain of the research is related to topics such as executive incentives, corporate digital transformation, corporate finance, innovation, mergers and acquisitions, financial risk, etc.
    6. Don't include any other information, only the JSON output in the specified format.

Example:
Input:
Title: “The Impact of Executive Incentives on Corporate Innovation: Evidence from Chinese Listed Firms”
Abstract: “This paper investigates the influence of executive incentives on corporate innovation by analyzing data from Chinese listed firms. The results show that equity-based incentives significantly improve innovation performance, while cash-based incentives show weaker effects.”

Output:
{{
  "keywords": [
    "高管激励",
    "企业创新",
    "股权激励"
  ]
}}

Here is the input:
Title: {title}
Abstract: {abstract}

Output:
"""


class Paper:
    def __init__(self, title, url, abstract, citation_count):
        self.title = title
        self.url = url
        self.abstract = abstract
        self.citation_count = citation_count
        self.keywords: list[str] = []
        self.related_chinese_papers: list[Paper] = []
    
    def keyword_decomposition(self):
        """
        对论文的标题和摘要进行关键词分解，分解成keywordsList
        """
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                print(f"Decomposing paper title: {self.title}")
                # 调用大模型进行处理
                groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
                response = groq.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{
                        "role": "user", 
                        "content": prompt.format(title=self.title, abstract=self.abstract)
                    }]
                )

                # Parse the JSON string into a list of keywords
                response_json = json.loads(response.choices[0].message.content)
                self.keywords = response_json["keywords"]
                return self.keywords
            except Exception as e:
                retry_count += 1
                print(f"Error occurred: {str(e)}")
                print(f"Retry attempt {retry_count} of {max_retries}")
                if retry_count == max_retries:
                    print("Max retries reached. Returning empty keywords list.")
                    self.keywords = []
                    return self.keywords
                continue
            
    def print_info(self):
        return {
            "title": self.title,
            "url": self.url,
            "citation_count": self.citation_count,
            "keywords": self.keywords,
            "related_chinese_papers": [paper.print_info() for paper in self.related_chinese_papers]
        }