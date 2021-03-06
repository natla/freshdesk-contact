import os

from dotenv import load_dotenv

# Initialise environment variables from .env
load_dotenv()

FRESHDESK_CONTACTS_ENDPOINT = 'https://{}.freshdesk.com/api/v2/contacts/'
FRESHDESK_TOKEN = os.getenv('FRESHDESK_TOKEN')

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USER_ENDPOINT = 'https://api.github.com/users/'
