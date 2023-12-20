import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re

nltk.download('punkt')
nltk.download('stopwords')

# Exception handling function
def handle_exception(url_id, action, exception):
    print(f"Error {action} for URL_ID {url_id}: {str(exception)}")

# Function to make a request to a URL and create a BeautifulSoup object
def get_soup(url, url_id):
    header = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=header)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except Exception as e:
        handle_exception(url_id, "making request", e)
        return None

# Function to write title and text to a file
def write_to_file(file_name, title, article):
    with open(file_name, 'w') as file:
        file.write(title + '\n' + article)

# Read the URL file into the pandas object
df = pd.read_excel('Input.xlsx')

# Loop through each row in the dataframe
for index, row in df.iterrows():
    url = row['URL']
    url_id = row['URL_ID']

    # Make a request to URL and create a BeautifulSoup object
    soup = get_soup(url, url_id)
    if soup is None:
        continue

    # Find title
    try:
        title = soup.find('h1').get_text()
    except Exception as e:
        handle_exception(url_id, "getting title", e)
        continue

    # Find text
    article = ""
    try:
        for p in soup.find_all('p'):
            article += p.get_text()
    except Exception as e:
        handle_exception(url_id, "getting text", e)

    # Write title and text to the file
    file_name = f'Text_Files/Data_Extraction_and_NLP{url_id}.txt'
    write_to_file(file_name, title, article)

# Directories
text_dir = "Text_Files"
stopwords_dir = "StopWords"
sentiment_dir = "MasterDictionary"

# Load all stop words from the stopwords directory and store in the set variable
stop_words = set()
for filename in os.listdir(stopwords_dir):
    with open(os.path.join(stopwords_dir, filename), 'r', encoding='ISO-8859-1') as f:
        stop_words.update(set(f.read().splitlines()))

# Load all text files from the directory and store in a list(docs)
docs = []
for text_file in os.listdir(text_dir):
    with open(os.path.join(text_dir, text_file), 'r') as f:
        text = f.read()
        # Tokenize the given text file
        words = word_tokenize(text)
        # Remove the stop words from the tokens
        filtered_text = [word for word in words if word.lower() not in stop_words]
        # Add each filtered tokens of each file into a list
        docs.append(filtered_text)

# Store positive and negative words from the directory
pos = set()
neg = set()

for filename in os.listdir(sentiment_dir):
    if filename == 'positive-words.txt':
        with open(os.path.join(sentiment_dir, filename), 'r', encoding='ISO-8859-1') as f:
            pos.update(f.read().splitlines())
    else:
        with open(os.path.join(sentiment_dir, filename), 'r', encoding='ISO-8859-1') as f:
            neg.update(f.read().splitlines())

# Now collect the positive and negative words from each file
# Calculate the scores from the positive and negative words
positive_words = []
negative_words = []
positive_score = []
negative_score = []
polarity_score = []
subjectivity_score = []

# Iterate through the list of docs
for i in range(len(docs)):
    positive_words.append([word for word in docs[i] if word.lower() in pos])
    negative_words.append([word for word in docs[i] if word.lower() in neg])
    positive_score.append(len(positive_words[i]))
    negative_score.append(len(negative_words[i]))
    polarity_score.append((positive_score[i] - negative_score[i]) / ((positive_score[i] + negative_score[i]) + 0.000001))
    subjectivity_score.append((positive_score[i] + negative_score[i]) / ((len(docs[i])) + 0.000001))

# Average Sentence Length, Percentage of Complex Words, Fog Index
avg_sentence_length = []
percentage_of_complex_words = []
fog_index = []
complex_word_count = []
avg_syllable_word_count = []

# Function to measure various text metrics
def measure(file):
    with open(os.path.join(text_dir, file), 'r') as f:
        text = f.read()
        # Remove punctuations
        text = re.sub(r'[^\w\s.]', '', text)
        # Split the given text file into sentences
        sentences = text.split('.')
        # Total number of sentences in a file
        num_sentences = len(sentences)
        # Total words in the file
        words = [word for word in text.split() if word.lower() not in stop_words]
        num_words = len(words)

        # Complex words having syllable count greater than 2
        complex_words = [word for word in words if sum(1 for letter in word if letter.lower() in 'aeiou') > 2]

        # Syllable Count Per Word
        syllable_count = sum(sum(1 for letter in word if letter.lower() in 'aeiou') for word in words)
        syllable_words = [word for word in words if sum(1 for letter in word if letter.lower() in 'aeiou') >= 1]

        avg_sentence_len = num_words / num_sentences
        avg_syllable_word_count = syllable_count / len(syllable_words)
        percent_complex_words = len(complex_words) / num_words
        fog_index = 0.4 * (avg_sentence_len + percent_complex_words)

        return avg_sentence_len, percent_complex_words, fog_index, len(complex_words), avg_syllable_word_count

# Iterate through each file or doc
for file in os.listdir(text_dir):
    x, y, z, a, b = measure(file)
    avg_sentence_length.append(x)
    percentage_of_complex_words.append(y)
    fog_index.append(z)
    complex_word_count.append(a)
    avg_syllable_word_count.append(b)

# Word Count and Average Word Length
word_count = []
average_word_length = []
for file in os.listdir(text_dir):
    with open(os.path.join(text_dir, file), 'r') as f:
        text = re.sub(r'[^\w\s]', '', f.read())
        words = [word for word in text.split() if word.lower() not in stop_words]
        length = sum(len(word) for word in words)
        average_word_length.append(length / len(words))
        word_count.append(len(words))

# Count Personal Pronouns
def count_personal_pronouns(file):
    with open(os.path.join(text_dir, file), 'r') as f:
        text = f.read()
        personal_pronouns = ["I", "we", "my", "ours", "us"]
        count = sum(len(re.findall(rf'\b{pronoun}\b', text)) for pronoun in personal_pronouns)
    return count

pp_count = [count_personal_pronouns(file) for file in os.listdir(text_dir)]

# Read the output data structure
output_df = pd.read_excel('Output Data Structure.xlsx')

# URL_ID 44, 57, 144 do not exist (i.e., pages do not exist, throw 404 error)
# so we are going to drop these rows from the table
output_df.drop([44 - 37, 57 - 37, 144 - 37], axis=0, inplace=True)

# These are the required parameters
variables = [positive_score,
              negative_score,
              polarity_score,
              subjectivity_score,
              avg_sentence_length,
              percentage_of_complex_words,
              fog_index,
              avg_sentence_length,
              complex_word_count,
              word_count,
              avg_syllable_word_count,
              pp_count,
              average_word_length]

# Write the values to the dataframe
for i, var in enumerate(variables):
    output_df.iloc[:, i + 2] = var

# Now save the dataframe to the disk
output_df.to_csv('Output_Data.csv')