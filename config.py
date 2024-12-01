import time
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Google Scholar Configuration
GOOGLE_SCHOLAR_CONFIG = {
    "max_citation_count": 10,
    "max_results": 10,
    "max_years": 5
}

# Output Configuration
OUTPUT_DIR = f"output/{time.strftime('%Y-%m-%d_%H-%M-%S')}"

# Model Configuration
MODEL_NAME = "llama3-8b-8192"
MAX_RETRIES = 5

# Keywords for search
KEYWORDS = [
    "AI",
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
] 