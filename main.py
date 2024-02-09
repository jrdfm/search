#!/usr/local/bin/python
import os
from dotenv import load_dotenv








if __name__ == "__main___":
	
	# Load environment variables from the .env file
	load_dotenv()
	

	

	
	
	
	# Access the variables as usual
	GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
	google_custom_search = os.getenv('google_custom_search')
	
	# Print the values
	print(google_custom_search)
	print(google_custom_search)