import os
from dotenv import load_dotenv
import wikipediaapi
from apiclient.discovery import build
import spacy.cli

def configure():
    load_dotenv()


configure()

#API Keys for Google Services
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
header = {'Accept':'application/json'}

#Wiki api
wiki_wiki = wikipediaapi.Wikipedia('en')

#Youtube api
youtube = build('youtube','v3',developerKey = GOOGLE_API_KEY)

#Semantic Analysis
api_token = os.getenv('SEMANTIC_API_KEY')
semantic_header = {"Authorization": f"Bearer {api_token}"}
API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"

#spacy.cli.download("en_core_web_lg")

nlp = spacy.load("en_core_web_md")
print("loading_model")

patent_api_key = os.getenv('PATENTVIEW_API_KEY')
patent_header = {
  'X-Api-Key':patent_api_key
}

