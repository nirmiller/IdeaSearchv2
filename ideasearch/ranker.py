from .variables import nlp, semantic_header, API_URL
import requests
import time
import numpy as np

'''
def get_semantic_simalirty(example_1, example_2):
  return web_model.predict([(example_1,example_2)])
'''


def get_semantic_similarity_request(example_1, example_2):
    r = {
        "inputs": {
            "source_sentence": example_1,
            "sentences": [example_2]
        }
    }

    response = requests.post(API_URL, headers=semantic_header, json=r)
    print(response.json()[0])
    return response.json()[0]


def get_semantic_similarity_list(example_1, list_1):

  r = {
            "inputs": {
                "source_sentence": example_1,
                "sentences":list_1
            }
      }
  response = requests.post(API_URL, headers=semantic_header, json=r)
  print("done")
  return response.json()

def get_word_similarity(test, compare):
  score = 0
  test_t = nlp(test)
  compare_t = nlp(compare)

  return test_t.similarity(compare_t)


def get_cos_similarity(test, compare):

    if test is not None and test != 'NA' and compare is not None and compare != 'NA':
        vec1 = nlp(test).vector
        vec2 = nlp(compare).vector
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    return 0
def score_query(search_algo, idea_query, threshold):

  searched_results = search_algo(idea_query)
  searched_ideas = score_list(iq=idea_query, queries_list=searched_results, threshold=threshold)
  return searched_ideas

def get_score(test, compare):
    score_1 = get_word_similarity(test, compare)
    score_2 = get_semantic_similarity_request(test, compare)
    print("SCORES: ", score_1, score_2, compare)
    return score_2 * score_1


def ranker(idea_query, compare_query):
    if not compare_query == None:

        idea = ""
        compare = ""
        if idea_query.description == "NA":
            idea = idea_query.title
        else:
            idea = idea_query.description

        if compare_query.description == "NA":
            compare = compare_query.title
        else:
            compare = compare_query.description

        return get_score(idea, compare)
    else:
        return 0


def score_list(iq, queries_list, threshold):

    title_qs = []
    desc_qs = []

    for q in queries_list:
        if q.description == None or not len(q.description) > 5:
            title_qs.append(q)
        else:
            desc_qs.append(q)

    title_qs_scores = []
    desc_qs_scores = []
    title_ws_scores = []
    desc_ws_scores = []


    if len(iq.title) > 2 and len(title_qs) > 0:
        title_qs_scores = get_semantic_similarity_list(iq.title, [obj.title for obj in title_qs])
        title_ws_scores = [get_word_similarity(obj.title, iq.title) for obj in title_qs]

    if len(iq.description) > 2 and len(desc_qs) > 0:
        desc_qs_scores = get_semantic_similarity_list(iq.description, [obj.description for obj in desc_qs])
        desc_ws_scores = [get_word_similarity(obj.description, iq.description) for obj in desc_qs]

    final_scores = []
    start = time.time()

    for i in range(len(title_qs_scores)):
        combined_t_score = title_qs_scores[i] * title_ws_scores[i]
        if combined_t_score > threshold:
            final_scores.append([title_qs[i], combined_t_score])
    for j in range(len(desc_qs_scores)):
        combined_d_score = desc_qs_scores[j] * desc_ws_scores[j]

        if combined_d_score > threshold:
            final_scores.append([desc_qs[j], combined_d_score])
    return final_scores
