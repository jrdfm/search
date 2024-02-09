#!/usr/bin/python3
import os
from dotenv import load_dotenv
import requests


# Load environment variables from the .env file
load_dotenv()


GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
google_custom_search = os.getenv('google_custom_search')
search_engine_id = os.getenv('search_engine_id')


import google.generativeai as genai
import google.ai.generativelanguage as glm

from google_labs_html_chunker.html_chunker import HtmlChunker
from google.ai import generativelanguage_v1beta as glvb
from urllib.request import urlopen
import json
service_account_file_name = 'service_account_key_.json'

from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(service_account_file_name)

scoped_credentials = credentials.with_scopes(
['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/generative-language.retriever'])





	





generative_client = glvb.GenerativeServiceClient(credentials=scoped_credentials)
# retriever_client = generativelanguage_v1beta.RetrieverServiceClient(credentials=scoped_credentials)
# permission_client = generativelanguage_v1beta.PermissionServiceClient(credentials=scoped_credentials)	

client = glvb.RetrieverServiceClient(credentials=scoped_credentials)


url_ = "https://www.googleapis.com/customsearch/v1"







def build_params(search_query, num = 10, start=1, dateRestrict='d1',**kwargs):
	params = { 'q': search_query, 
		   	   'key': google_custom_search, 
			   'cx': search_engine_id,
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



'''____________________________________________________________________________'''
	
def sample_list_corpora(list_doc = False):
	# Initialize request argument(s)
	request = glvb.ListCorporaRequest(
	)
	
	# Make the request
	page_result = client.list_corpora(request=request)
	ls = []
	# Handle the response
	for response in page_result:
		print(name := response.name)
		ls.append(name)
		if list_doc: sample_list_documents(name)
	return ls

def sample_list_documents(parent):
	# Initialize request argument(s)
	request = glvb.ListDocumentsRequest(
		parent=parent,
	)
	# Make the request
	page_result = client.list_documents(request=request)
	# Handle the response
	for response in page_result:
		print(f'	{response.name}')


def sample_query_corpus(name, q, n):
	# Initialize request argument(s)
	request = glvb.QueryCorpusRequest(
		name="name_value",
		query="query_value",
	)
	request = glvb.QueryCorpusRequest(name=name,
								query=q,
								results_count=n)
	# Make the request
	response = client.query_corpus(request=request)
	
	# Handle the response
	return response

def aqa_query(corpus_name, q, n, answer_style):
	MODEL_NAME = "models/aqa"
	answer_style = answer_style
	content = glvb.Content(parts=[glvb.Part(text=q)])
	retriever_config = glvb.SemanticRetrieverConfig(source=corpus_name, query=content)
	req = glvb.GenerateAnswerRequest(model=MODEL_NAME,
									contents=[content],
									semantic_retriever=retriever_config,
									answer_style=answer_style)
	aqa_response = generative_client.generate_answer(req)
	# print(aqa_response)	
	js = json.dumps(aqa_response)
	print(js)
	# for content in aqa_response:
	# 	print(content)
	return aqa_response


def sample_delete_corpus(corpus_name):
	# Initialize request argument(s)
	request = glvb.DeleteCorpusRequest(
		name=corpus_name,
		force=True
	)
	# Make the request
	client.delete_corpus(request=request)
	print("Successfully deleted corpus: " + corpus_name)


def del_all_corpus(corpus_ls):
	for c in corpus_ls:
		sample_delete_corpus(c)

def create_corpus(name = "default"):
	corpus_ = glvb.Corpus(display_name=name)
	# Initialize request argument(s)
	request = glvb.CreateCorpusRequest(corpus = corpus_
	)
	# Make the request
	response = client.create_corpus(request=request)

	# Handle the response
	return response.name

def create_document(corpus_name, doc_name, url):
	doc = glvb.Document(display_name=doc_name)
	# Add metadata.
	document_metadata = [glvb.CustomMetadata(key="url", string_value=url)]
	doc.custom_metadata.extend(document_metadata)
	# Initialize request argument(s)
	request = glvb.CreateDocumentRequest(
		parent=corpus_name,
		document=doc)

	# Make the request
	response = client.create_document(request=request)
	
	# Handle the response
	return response.name

def batch_create_chunks(doc_name, url):

	try:
		with urlopen(url, timeout=0.5) as f:
			html = f.read().decode('utf-8')
			chunker = HtmlChunker(
				max_words_per_aggregate_passage=200,
				greedily_aggregate_sibling_nodes=True,
				html_tags_to_exclude={"noscript", "script", "style"},)
			passages  = chunker.chunk(html)
	except Exception as e:
		# pass
		print(f'ERROR: {e}')
		# passages = [html]
	
	# Create `Chunk` entities.
	chunks = []
	for passage in passages:
		chunk = glm.Chunk(data={'string_value': passage})
		chunks.append(chunk)
    # Initialize request argument(s)
	create_chunk_requests = []
	for chunk in chunks:
		create_chunk_requests.append(glvb.CreateChunkRequest(parent=doc_name, chunk=chunk))

	request = glvb.BatchCreateChunksRequest(parent=doc_name, requests=create_chunk_requests)
	# Make the request
	response = client.batch_create_chunks(request=request)

	# Handle the response
	# print(response)

	# your_module.py
def fun(user_query):
	# Your implementation here
	# Return the text response in Markdown format
	return "### Hello, *Markdown* World!"


if __name__ == "__main__":
	

	
	genai.configure(api_key=GOOGLE_API_KEY)
	
	
	
	


	# answer_style = "VERBOSE" # Or "ABSTRACTIVE", EXTRACTIVE
	
	corpus_ls = sample_list_corpora(True)
	# del_all_corpus(corpus_ls)
	print(f'corpus_ls {corpus_ls}')
	if not corpus_ls: 
		corpus_name = create_corpus()
	else:
		corpus_name = corpus_ls[0]
	
	print(f'corpus_name: {corpus_name}')
	q = "What did putin and Tucker discuss?"
	url = "https://time.com/6693098/vladimir-putin-tucker-carlson-interview-ukraine-gershkovich/"

	

	response = google_search(build_params(q,num = 10))
	for i in response['items']:
		url, display_name = i['link'], i['title']
		# print(f"URL : {url}  display_name : {display_name}\n")
	try:
		doc_n = create_document(corpus_name, display_name, url)
		batch_create_chunks(doc_n, url)
		# ingest_document(corpus_resource_name, display_name, url)
	except Exception as e:
		# ...
		print(e)

	# corpus_name = corpus_ls[0]
	# sample_query_corpus(corpus_name,q,5)
	
	# doc_n = create_document(corpus_name, "putin_tucker", url)
	
	# print(doc_n)
	
	# print(f'create batch chunks for {doc_n}')
	# batch_create_chunks(doc_n, url)
	ret = sample_query_corpus(corpus_name,q,10)
		
	# string = "Compose an essay-style response. Trim irrelevant \
	# content from the provided text, concentrating on the query: " + q + ". Deliver a minimum of three insightful \
	# 	sub-paragraphs,not in a list form. The text to be refined is:"
	qu = "Query: " + q
	prompt = "Compose a VERBOSE essay-styled response. Deliver a minimum of three insightful \
		sub-paragraphs. Trim irrelevant content from the provided Text, concentrating on the Query.\
			Don't use numbered lists in the response paragraph"
	

	
	# text = "The text to be refined is:"
	
	text = "The text to be refined is:\n" + ''.join(chunk.chunk.data.string_value for chunk in ret.relevant_chunks if chunk.chunk.data.string_value)
	
	
	model = genai.GenerativeModel('gemini-pro')

	
	file_path = 'prompt.text'

	with open(file_path, 'r') as file:
		prompt = file.read()
	
	
	content = glvb.Content(parts=[glvb.Part(text=prompt), glvb.Part(text=qu), glvb.Part(text=text)])
	response = model.generate_content(contents=[content], stream = True)
	
	print(42*"__")
	# print(response.text)
	
	# for chunk in response:
	# 	print(chunk.text)
	response.resolve()
	print(response.text)
	print(f'\n')
	




	
	
	
	
