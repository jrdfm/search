#!/usr/bin/python3
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# Load environment variables from the .env file
load_dotenv()


GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
google_custom_search = os.getenv('google_custom_search')
search_engine_id = os.getenv('search_engine_id')

search_en_id = os.getenv('search_en_id')
api_key = os.getenv('api_key')

import google.generativeai as genai
import google.ai.generativelanguage as glm

from google_labs_html_chunker.html_chunker import HtmlChunker
from google.ai import generativelanguage_v1beta as glvb
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from urllib.request import urlopen
import json
service_account_file_name = 'service_account_key_.json'

from google.oauth2 import service_account


credentials = service_account.Credentials.from_service_account_file(service_account_file_name)

scoped_credentials = credentials.with_scopes(
['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/generative-language.retriever'])



generative_client = glvb.GenerativeServiceClient(credentials=scoped_credentials)

client = glvb.RetrieverServiceClient(credentials=scoped_credentials)


url_ = "https://www.googleapis.com/customsearch/v1"

def build_params(search_query, num = 10, start=1, dateRestrict='d1',**kwargs):
	params = { 'q': search_query, 
		   	   'key': api_key, 
			   'cx': search_en_id,
			   'num': num,
			   'start': 1,
			   'dateRestrict': 'd1',
			   }
	params.update(kwargs)
	return params

def google_search(params):
	response = requests.get(url_, params=params)
	if response.status_code != 200:
		raise Exception('API response: {}'.format(response.status_code))
	return response.json()


def html_txt( url):
	html = None
	try:
		with urlopen(url, timeout=0.5) as f:
			html = f.read().decode('utf-8')
	except Exception as e:
		try:
			headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:77.0) Gecko/20190101 Firefox/77.0'}
			html_content = requests.get(url, headers=headers, timeout= 2).content
			html = html_content.decode('utf-8')
		except Exception as e:
			print(f'{e} {url}')
	rel_txt = get_plain_text(html)if html else ""
	return rel_txt

import requests
from readabilipy import simple_json_from_html_string
req = requests.get('https://en.wikipedia.org/wiki/Readability')
article = simple_json_from_html_string(req.text, use_readability=True)

def html_txt(url):
    html = None
    try:
        response = requests.get(url, timeout=0.5)
        html = response.text
    except Exception as e:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:77.0) Gecko/20190101 Firefox/77.0'}
            html_content = requests.get(url, headers=headers, timeout=2).content
            html = html_content.decode('utf-8')
        except Exception as e:
            print(f'{e} {url}')
    rel_txt = get_plain_text(html) if html else ""
    return rel_txt




def get_plain_text(html):
	soup = BeautifulSoup(html, features='lxml')
	return soup.getText().strip()

from bs4 import BeautifulSoup

def get_plain_text(html):
    """
    Extract plain text from HTML.

    Args:
        html: The HTML to extract plain text from.

    Returns:
        A string containing the plain text.
    """
    
    # Create a BeautifulSoup object.
    soup = BeautifulSoup(html, features='lxml')

    # Remove all script and style tags.
    for script in soup.find_all('script'):
        script.extract()
    for style in soup.find_all('style'):
        style.extract()

    # Get the text from the BeautifulSoup object.
    text = soup.get_text()

    # Strip leading and trailing whitespace from the text.
    text = text.strip()

    # Return the plain text.
    return text

def run(q):
	response = google_search(build_params(q,num = 10))
	
	data = []
	res = ""
	for i in response['items']:
		url, display_name = i['link'], i['title']
		print(f"URL : {url}  display_name : {display_name}\n")
		result = html_txt(url)
		res += result
		data.append((url, display_name, result))
		# print(result)
	
	# df = pd.DataFrame(data, columns=["Url","Display Name","Result"])
	# # print(df)
	# df.to_csv("output.csv")
	
	print(res)
	concatenated_text = "Chunks:" + res
	
	model = genai.GenerativeModel('gemini-pro', safety_settings={
	HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
	HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
	HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
	HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
	})
	prompt = "Give a verbose summary of following text from a web search based on the query. \
		  Return a markdown in a paragraph form with at least 3 paragraphs\
		  The text is after the token Text: \
		  The query is after the token Query: "
	prompt = "Respond in an essay form with a title and summary at the end. Remove irrelevant \
	parts from the following text with respect to the query : " + q + ". Return at least 3 detailed sub paragraphs \n"
	prompt = "Given a query and a text, provide a detailed and verbose summary of the text in markdown format. \
		   The summary should be at least 3 paragraphs and 10000 words long and should be based on the query."
	# print(f'{concatenated_text}')
	content = glvb.Content(parts=[glvb.Part(text=prompt), glvb.Part(text=q), glvb.Part(text=concatenated_text)])
	# content = glvb.Content(parts=[glvb.Part(text=prompt), glvb.Part(text=q)])
	# response = model.generate_content(contents=content, stream = True)
	response = model.generate_content(contents=content, stream = True)
	print(42*"__")
	# print(response.text)
	response.resolve()
	for chunk in response:
		print(chunk.text)
	
	# print(response.text)
	# print(f'\n')
	return response.text


if __name__ == "__main__":
	q = 'Trump news'
	q = "Putin Tucker"
	q = "What did putin and Tucker discuss?"
	q = "What is the plot of Tenet?"
	run(q)
	
