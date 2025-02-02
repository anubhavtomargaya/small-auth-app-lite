import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"
EMBEDDING_DIMENSION = 1536  # Ada-002 embedding dimension

# DBSCAN Configuration
DBSCAN_EPS = 0.3  # Distance threshold for DBSCAN
DBSCAN_MIN_SAMPLES = 2  # Minimum samples per cluster

# Category Mapping
CATEGORY_MAPPING = {
    0: 'A',
    1: 'B',
    2: 'C',
    -1: 'D'  # Noise points in DBSCAN
} 