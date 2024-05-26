import openai
import os
import requests
import pprint
import re

from dotenv import load_dotenv

load_dotenv()

MW_DICTIONARY_API_KEY = os.getenv('MW_DICTIONARY_API_KEY')
MW_THESAURUS_API_KEY = os.getenv('MW_THESAURUS_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
MODEL = "gpt-4o"

openai.api_key = OPENAI_API_KEY


def chatgpt_request(system_prompt=None, user_prompt=None, max_tokens=50):
    try:
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": ""}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Not available"


def parse_numbered_examples(numbered_examples):
    parsed_examples = '<br>'.join(re.findall(r"\d+\.\s+.+", numbered_examples))
    return parsed_examples


def higlight_word_in_examples(examples, word):
    # Escape special characters in the word
    escaped_word = re.escape(word)
    # Create a regular expression to find the word and its variations
    regex = re.compile(rf'({escaped_word}\w*)', re.IGNORECASE)
    # Replace the word with a highlighted version
    highlighted = regex.sub(r'<span class="highlight">\1</span>', examples)
    return highlighted


def get_5_examples(word):
    prompt = f"""Provide an answer with only five sentences using different forms and tenses of the word {word}' in different contexts. 
    Highlight this word adding <span class="highlight"></span>:

    1.
    2.
    3.
    4.
    5.
    """
    numbered_examples = chatgpt_request(system_prompt=prompt, max_tokens=150)
    parsed_numbered_examples = parse_numbered_examples(numbered_examples)
    return parsed_numbered_examples


def get_difinition(word):
    prompt = f"Define the word '{word}':"
    definition = chatgpt_request(system_prompt=prompt, max_tokens=30)
    return definition


def get_translation(word):
    prompt = f"Translate the word '{word}' to Russian:"
    translation = chatgpt_request(system_prompt=prompt, max_tokens=30)
    return translation


def get_synonyms(word):
    prompt = f"Provide 1-3 synonyms of the word '{word}':"
    translation = chatgpt_request(system_prompt=prompt, max_tokens=30)
    return translation


def api_request(url):
    return requests.get(url=url)


def dictionary_api_request(word):
    url = f"https://dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={MW_DICTIONARY_API_KEY}"
    response_json = api_request(url).json()
    shortdef = response_json[0]["shortdef"]
    # def1 = response_json[0]["def"][0]["sseq"][0][0][1][1][1]["dt"][0][1]
    # def2 = response_json[0]["def"][0]["sseq"][0][0][1][1][1]["dt"][0][1]
    return shortdef


def thesaurus_api_request(word):
    url = f"https://dictionaryapi.com/api/v3/references/thesaurus/json/{word}?key={MW_THESAURUS_API_KEY}"
    response_json = api_request(url).json()
    shortdef = response_json[0]["shortdef"] # list
    return shortdef

# class Bot:
#
#     def __init__(self):
#         self.bot = OpenAI(api_key=OPENAI_API_KEY)
#
#     def send_multiple_messages(self, *args) -> str:
#         """
#         :type messages: dict {role1: content1, role2: content2, ..., roleN: contentN}]
#         """
#         m = []
#         for message in args:
#             role = message["role"]
#             content = message["content"]
#             m.append({"role": role, "content": content})
#
#         completion = self.bot.chat.completions.create(
#             model=model,
#             messages=m
#         )
#
#         return completion.choices[0].message.content


if __name__ == "__main__":
    print(pprint.pprint(dictionary_api_request("test"), compact=True))
    print(pprint.pprint(thesaurus_api_request("test"), compact=True))