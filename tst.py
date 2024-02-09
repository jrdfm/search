#!/usr/bin/python3
import os
from dotenv import load_dotenv
import requests


# Load environment variables from the .env file
load_dotenv()


GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
google_custom_search = os.getenv('google_custom_search')
search_engine_id = os.getenv('search_engine_id')




url = "https://www.googleapis.com/customsearch/v1"







def build_params(search_query, num = 2, start=1, dateRestrict='d1',**kwargs):
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
	response = requests.get(url, params=params)
	if response.status_code != 200:
		raise Exception('API response: {}'.format(response.status_code))
	return response.json()



def create_corpus(name = "default"):
	# Create a corpus.
	corpus_ = glm.Corpus(display_name=name)
	create_corpus_request = glm.CreateCorpusRequest(corpus=corpus_)
	
	# Make the request
	create_corpus_response = retriever_service_client.create_corpus(create_corpus_request)
	
	# Set the `corpus_resource_name` for subsequent sections.
	corpus_resource_name = create_corpus_response.name
	get_corpus_request = glm.GetCorpusRequest(name=corpus_resource_name)
	get_corpus_response = retriever_service_client.get_corpus(get_corpus_request)
	
	return corpus_ , corpus_resource_name, get_corpus_response



def ingest_document(corpus_resource_name, display_name, url):
	doc = glm.Document(display_name=display_name)
	# Add metadata.
	document_metadata = [glm.CustomMetadata(key="url", string_value=url)]
	doc.custom_metadata.extend(document_metadata)
	
	# Make the request
	create_document_request = glm.CreateDocumentRequest(parent=corpus_resource_name, document=doc)
	create_document_response = retriever_service_client.create_document(create_document_request)
	
	# Set the `document_resource_name` for subsequent sections.
	document_resource_name = create_document_response.name
	# print(f'create_document_response: {create_document_response} 		document_resource_name:{document_resource_name}')

	
	try:
		with urlopen(url, timeout=0.15) as f:
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
	
	# Make the request
	create_chunk_requests = []
	for chunk in chunks:
		create_chunk_requests.append(glm.CreateChunkRequest(parent=document_resource_name, chunk=chunk))
	request = glm.BatchCreateChunksRequest(parent=document_resource_name, requests=create_chunk_requests)
	response = retriever_service_client.batch_create_chunks(request)
	# print(response)
	# Make the request
	# request = glm.ListChunksRequest(parent=document_resource_name, page_size=15)
	# list_chunks_response = retriever_service_client.list_chunks(request)
	# for index, chunks in enumerate(list_chunks_response.chunks):
	# 	print(f'\nChunk # {index + 1}')
	# 	print(f'Resource Name: {chunks.name}')
	# 	# Only ACTIVE chunks can be queried.
	# 	print(f'State: {glm.Chunk.State(chunks.state).name}')
	return document_resource_name, create_document_response



if __name__ == "__main__":
	
	import pathlib
	import textwrap
		
	import json
	import google.generativeai as genai
	from google_labs_html_chunker.html_chunker import HtmlChunker
	from google.ai import generativelanguage_v1beta
	from urllib.request import urlopen
	
	service_account_file_name = 'service_account_key_.json'
	
	from google.oauth2 import service_account
	
	credentials = service_account.Credentials.from_service_account_file(service_account_file_name)
	
	scoped_credentials = credentials.with_scopes(
	['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/generative-language.retriever'])

	
	import google.ai.generativelanguage as glm
	generative_service_client = glm.GenerativeServiceClient(credentials=scoped_credentials)
	retriever_service_client = glm.RetrieverServiceClient(credentials=scoped_credentials)
	permission_service_client = glm.PermissionServiceClient(credentials=scoped_credentials)



		
	
	

	# print(results['items'][0]['link'])
	# print(results['items'][0]['snippet'])
	
	# print(google_search(build_params('whats the meaning of life'))['items'][0]['link'])
	
	
	# genai.configure(api_key=GOOGLE_API_KEY)
	
	# for m in genai.list_models():
	# 	if 'generateContent' in m.supported_generation_methods:
	# 		print(m.name)
	
	
	
	# model = genai.GenerativeModel('gemini-pro')
	# response = model.generate_content("What is the meaning of life?")
	
	# print(response.text)
	

	
	
	
	genai.configure(api_key=GOOGLE_API_KEY)
	
	
	q = 'Trump news'
	q = "Putin Tucker"
	q = "What did putin and Tucker discuss?"
	response = google_search(build_params(q,num = 10))
	
	corpus_ , corpus_resource_name, get_corpus_response = create_corpus("test")
	# Set force to False if you don't want to delete non-empty corpora.
	
	
	
	for i in response['items']:
		url, display_name = i['link'], i['title']
		print(f"URL : {url}  display_name : {display_name}\n")
		try:
			ingest_document(corpus_resource_name, display_name, url)
		except Exception as e:
			# ...
			print(e)
		# # ingest_document(corpus_resource_name, display_name, url)
	
	user_query = "What happened at todays supreme court hearing about Trump?"
	user_query = "What did putin and Tucker discuss?"
	results_count = 10
	
	request = glm.QueryCorpusRequest(name=corpus_resource_name,
									query=user_query,
									results_count=results_count)
	query_corpus_response = retriever_service_client.query_corpus(request)
	# print(query_corpus_response)
	# parse query_corpus_response and print string_value
	# string = "Respond in an essay form with a title and summary at the end. Remove irrelevant parts from the following text with respect to the query : " + user_query + ". Return at least 3 detailed sub paragraphs \n"
	string = "Compose an essay-style response with a title and summary at the conclusion. Eliminate extraneous content \
		from the given text, focusing on the query: " + user_query + ". Present a minimum of three informative sub-paragraphs\
			without explicitly stating the Title, summary and sub-paragraphs fields in the response. Text: "
	string = "Compose an essay-style response, encompassing a title and summarizing remarks at the conclusion. Trim irrelevant \
		content from the provided text, concentrating on the query: " + user_query + ". Deliver a minimum of three insightful \
			sub-paragraphs,not in a list form, without explicitly mentioning titles, summaries, or sub-paragraphs in the response. The text to be refined is:"
	string = "Compose an essay-style response. Trim irrelevant \
		content from the provided text, concentrating on the query: " + user_query + ". Deliver a minimum of three insightful \
			sub-paragraphs,not in a list form. The text to be refined is:"
	for chunk in query_corpus_response.relevant_chunks:
		string_value = chunk.chunk.data.string_value
		if string_value:
			string += string_value
	# print(string)
	
	model = genai.GenerativeModel('gemini-pro')
	# response = model.generate_content("What was todays supreme court hearing about?")
	response = model.generate_content(string, stream = False)
	
	print(42*"__")
	print(response.text)
	# for chunk in response:
	# 	print(response.text)
	print(f'\n')
	

	
	
	# user_query = "What is the purpose of Project IDX?"
	answer_style = "VERBOSE" # Or "ABSTRACTIVE", EXTRACTIVE
	MODEL_NAME = "models/aqa"
	
	# Make the request
	# corpus_resource_name is a variable set in the "Create a corpus" section.
	# content = glm.Content(parts=[glm.Part(text=user_query)])
	# retriever_config = glm.SemanticRetrieverConfig(source=corpus_resource_name, query=content)
	# req = glm.GenerateAnswerRequest(model=MODEL_NAME,
	# 								contents=[content],
	# 								semantic_retriever=retriever_config,
	# 								answer_style=answer_style)
	# aqa_response = generative_service_client.generate_answer(req)
	# print(aqa_response)	
	
	# generative_client = generativelanguage_v1beta.GenerativeServiceClient(credentials=scoped_credentials)
	# retriever_client = generativelanguage_v1beta.RetrieverServiceClient(credentials=scoped_credentials)
	# permission_client = generativelanguage_v1beta.PermissionServiceClient(credentials=scoped_credentials)	
	
	# def sample_list_corpora():
	# 	# Create a client
	# 	client = generativelanguage_v1beta.RetrieverServiceClient(credentials=scoped_credentials)
		
	# 	# Initialize request argument(s)
	# 	request = generativelanguage_v1beta.ListCorporaRequest(
	# 	)
		
	# 	# Make the request
	# 	page_result = client.list_corpora(request=request)
		
	# 	# Handle the response
	# 	for response in page_result:
	# 		print(response)
	
	# sample_list_corpora()
	

	req = glm.DeleteCorpusRequest(name=corpus_resource_name, force=True)
	delete_corpus_response = retriever_service_client.delete_corpus(req)
	print("Successfully deleted corpus: " + corpus_resource_name)