import os
from dotenv import load_dotenv

load_dotenv()


MAX_PAGE_DETAILS_LENGTH = int(os.getenv("MAX_PAGE_DETAILS_LENGTH", 2048))
