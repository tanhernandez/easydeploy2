# settings.py
from os.path import join, dirname, realpath
from dotenv import load_dotenv  # pip install python-dotenv
import os

dotenv_path = dirname(realpath(__file__)) + '\\.env'
# OR, the same with increased verbosity:
load_dotenv(dotenv_path)

# Map the values the needs to be public
DEV_BRANCH = os.environ.get("DEV_BRANCH")
DEV_IP = os.environ.get("DEV_IP")
DEV_PATH = os.environ.get("DEV_PATH")

STAGE_BRANCH = os.environ.get("STAGE_BRANCH")
STAGE_IP = os.environ.get("STAGE_IP")
STAGE_PATH = os.environ.get("STAGE_PATH")

PROD_BRANCH = os.environ.get("PROD_BRANCH")
PROD_IP = os.environ.get("PROD_IP")
PROD_PATH = os.environ.get("PROD_PATH")

PUBLIC_SSH_KEY = os.environ.get("PUBLIC_SSH_KEY")

