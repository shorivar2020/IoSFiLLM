import yaml
from dotenv import load_dotenv
# Load configuration
config = yaml.safe_load(open('config.yaml'))
env = load_dotenv()

ALLOWED_EXTENSIONS = {'txt', 'pdf'}
file_dir = 'uploads/'

TIMEOUT_LENGTH = 60
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/93.0.4577.63 Safari/537.36"
)
TIMEOUT = 10  # Default timeout in seconds
HTTP_STATUS_SUCCESS = 200
MIN_TEXT_LENGTH = 30  # Minimum length of text to accumulate
HTML_TAGS = ['p', 'div', 'span', 'h1', 'h2', 'h3', 'li']
GOOGLE_API_URL = 'https://www.googleapis.com/customsearch/v1'
TIME_SLEEPING = 10
BING_API_LINK = "https://api.search.brave.com/res/v1/web/search"
PUBMED_LINK_API = "https://pubmed.ncbi.nlm.nih.gov/"
