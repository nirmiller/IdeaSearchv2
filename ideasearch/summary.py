import string
import re
import openai
from .variables import OPENAI_API_KEY, nlp, grammar_checker



def clean_up_string(str_sam):
  pattern = r'[' + string.punctuation + ']'
  entry_string = re.sub(pattern, '', str_sam)
  result = grammar_checker.edits(entry_string, session_id='test_session', auto_apply=True)['applied_text']
  print('AHHH', result)
  return result

def get_keywords(idea):
  idea_nlp = nlp(idea)
  prominent_key_words = []

  keywords = []
  keyword_relationships = []

  for token in idea_nlp:
      if token.dep_ not in ("punct", "det"):
          if token.pos_ in ("NOUN", "PROPN"):
              keywords.append(token)

  output = ""
  for i in range(len(keywords)):
    if i < len(keywords)-1:

      output += f"{keywords[i]} OR "
    else:
      output += f"{keywords[i]}"

  return output

def summarize_title(idea):

  text = clean_up_string(idea)
  keywords = get_keywords(idea)

  openai.api_key = OPENAI_API_KEY
  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "user", "content": f"Summarize into a short effective google search, max length 20 words, this text : {text} while keeping in mind and using some of these keywords : {keywords}"}
    ]
  )
  print(clean_up_string(completion.choices[0].message['content']))
  #run abstractive summarization
  return clean_up_string(completion.choices[0].message['content'])