#!/usr/bin/python3

import os
from dotenv import load_dotenv



service_account_file_name = 'service_account_key.json'

from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(service_account_file_name)

scoped_credentials = credentials.with_scopes(
['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/generative-language.retriever'])


import google.ai.generativelanguage as glm

generative_service_client = glm.GenerativeServiceClient(credentials=scoped_credentials)
retriever_service_client = glm.RetrieverServiceClient(credentials=scoped_credentials)
permission_service_client = glm.PermissionServiceClient(credentials=scoped_credentials)





example_corpus = glm.Corpus(display_name="Google for Developers Blog")
create_corpus_request = glm.CreateCorpusRequest(corpus=example_corpus)

# Make the request
create_corpus_response = retriever_service_client.create_corpus(create_corpus_request)

# Set the `corpus_resource_name` for subsequent sections.
corpus_resource_name = create_corpus_response.name




get_corpus_request = glm.GetCorpusRequest(name=corpus_resource_name)

# Make the request
get_corpus_response = retriever_service_client.get_corpus(get_corpus_request)

# Print the response
# print(get_corpus_response)


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


def ingest_document(corpus_resource_name, document, display_name, url):
	doc = glm.Document(display_name=display_name)
	# Add metadata.
	document_metadata = [glm.CustomMetadata(key="url", string_value=url)]
	doc.custom_metadata.extend(document_metadata)
	
	# Make the request
	create_document_request = glm.CreateDocumentRequest(parent=corpus_resource_name, document=document)
	create_document_response = retriever_service_client.create_document(create_document_request)

	# Set the `document_resource_name` for subsequent sections.
	document_resource_name = create_document_response.name
	return document_resource_name, create_document_response



# Create a document with a custom display name.
example_document = glm.Document(display_name="Introducing Project IDX, An Experiment to Improve Full-stack, Multiplatform App Development")

# Add metadata.
# Metadata also supports numeric values not specified here
document_metadata = [
    glm.CustomMetadata(key="url", string_value="https://developers.googleblog.com/2023/08/introducing-project-idx-experiment-to-improve-full-stack-multiplatform-app-development.html")]
example_document.custom_metadata.extend(document_metadata)

# Make the request
# corpus_resource_name is a variable set in the "Create a corpus" section.
create_document_request = glm.CreateDocumentRequest(parent=corpus_resource_name, document=example_document)
create_document_response = retriever_service_client.create_document(create_document_request)

# Set the `document_resource_name` for subsequent sections.
document_resource_name = create_document_response.name
print(create_document_response)

from google_labs_html_chunker.html_chunker import HtmlChunker

from urllib.request import urlopen



def chunk_html(url):
	with urlopen(url) as f:
		html = f.read().decode('utf-8')
		chunker = HtmlChunker(
			max_words_per_aggregate_passage=100,
			greedily_aggregate_sibling_nodes=False)
		passages  = chunker.chunk(html)
	
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
	print(response)
		



# if __name__ == '__main__':
# 	# print(create_corpus_response)
# 	# print(get_corpus_response)

	
