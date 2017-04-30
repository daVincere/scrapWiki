#import rependencies

# library for pulling out data from html and xml
from bs4 import BeautifulSoup

# HTTP library that deals with requests in python
# pull, push, authenticate
import requests

# for regular expression operations
import re

# intrinsic opertations in python such as
# addition, comparision, >, < operations
import operator

# a format of pulling data from the web
import json

# takes a list and creates a table out of it
from tabulate import tabulate

import sys

# words that do not have any value
from stop_words import get_stop_words


# get the words
def getWordList(url):
	word_list = []
	# get raw data from the url
	source_code = requests.get(url)
	# convert to text
	plain_text = source_code.text
	# lxml format
	soup = BeautifulSoup(plain_text, 'lxml')

	# find the words in paragraph tag (html)
	for text in soup.findAll('p'):
		if text.text is None:
			continue
		# content
		content = text.text

		# lowercase and split into array
		words = content.lower().split()

		# for each word
		for word in words:
			# remove non-chars
			cleaned_word = clean_word(word)
			# if there is still something there
			if len(cleaned_word) > 0:
				# add it to our word list
				word_list.append(cleaned_word)


	return word_list

# clean word with regex
def clean_word(word):
	cleaned_word = re.sub('A-Za-z]+', '', word)
	return cleaned_word


def createFrequencyTable(word_list):
	word_count = {}
	
	for word in word_list:
		# indexing the words
		if word in word_count:
			word_count[word]+=1
		else:
			word_count[word] = 1
		
	return word_count


# remove stop words
def remove_stop_words(frequency_list):
	# stop words from english language for now
	stop_words = get_stop_words('en')

	# empty temporary list of stop words
	temp_list = []
	for key, value in frequency_list:
		if key not in stop_words:
			temp_list.append([key, value])

	return temp_list






wikipedia_api_link = "https://en.wikipedia.org/w/api.php?format=json&action=query&list=search&srsearch="

wikipedia_link = "https://en.wikipedia.org/wiki/"

if(len(sys.argv)<2):
	print "enter a valid string"
	exit()

# get the search word
string_query = sys.argv[1]

if(len(sys.argv) > 2):
	search_mode = True
else:
	search_mode = False

# create our url
url = wikipedia_api_link + string_query

try:
	response = requests.get(url)

	# data contains the json data that came from the query link
	data = json.loads(response.content.decode('utf-8'))

	# format this data
	wikipedia_page_tag = data['query']['search'][0]['title']

	# create a new url
	url = wikipedia_link + wikipedia_page_tag

	# gets the list of words from the page
	page_word_list = getWordList(url)

	# create a table of word counts
	page_word_count = createFrequencyTable(page_word_list)

	# sort the table by frequency count
	# defined a variable key as the first word
	sorted_word_frequency_list = sorted(page_word_count.items(), key=operator.itemgetter(1), reverse=True)

	# remove stop words
	if(search_mode):
		sorted_word_frequency_list = remove_stop_words(sorted_word_frequency_list)

	# sum the total words to calculate the frequencies
	total_words_sum = 0

	for key, value in sorted_word_frequency_list:
		total_words_sum = total_words_sum + value

	# just get the top 20 words
	if len(sorted_word_frequency_list) > 20:
		sorted_word_frequency_list = sorted_word_frequency_list[:20]

	# create our final list, words + frequency + percentage
	final_list = []

	for key, value in sorted_word_frequency_list:
		percentage_value = float(value *100)/total_words_sum
		# values get added to a list, finallist
		final_list.append([key, value, round(percentage_value, 4)])

	# header for tables 
	print_headers = ['Word', 'Frequency', 'Frequency Percentage',]

	# print the table with tabulate
	# gets data from final_list,
	# header titles from print_headers and 
	# with a table format
	print tabulate(final_list, headers=print_headers, tablefmt='orgtbl')


except requests.exceptions.Timeout:
	print("Didn't work. Try again!")