from .search import searcher, get_patent_query, get_google_query, get_youtube_query, get_scholar_query
from .ranker import ranker, score_list, score_query, get_cos_similarity
from .utils import query
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED


def tree_search(idea_query, threshold, max_depth):
    max_length = 25
    memorization = []
    search = []

    def tree_ranking(input, threshold, max_depth, current_depth, idea_query):
        try:
            if current_depth > max_depth:
                return
            if current_depth == 0:
                tree_ranking(searcher(idea_query), threshold, max_depth, 0 + 1, idea_query)
            else:

                future_search = []

                for prompt in input:
                    if prompt.title not in memorization:
                        try:
                            score = ranker(idea_query, prompt)
                        except:
                            score = 0
                        if score >= threshold:
                            future_search.append([prompt, score])
                    memorization.append(prompt.title)
                print('future', len(future_search))

                future_search = sorted(future_search, key=lambda x: 1 / x[1])
                if len(future_search) < max_length:
                    for i in range(len(future_search)):
                        search.append(future_search[i])
                else:
                    for i in range(max_length):
                        search.append(future_search[i])
                for prompt in future_search:
                    if isinstance(prompt, query):
                        tree_ranking(searcher(prompt), threshold, max_depth, current_depth + 1, idea_query)


        except Exception as e:
            print(e)
            return

    tree_ranking([], threshold, max_depth, 0, idea_query)
    search += searcher_patent(idea_query, threshold)
    print(len(memorization))
    return sorted(search, key=lambda x: 1 / x[1])


def searcher_patent(idea_query, threshold):
    patents = get_patent_query(idea_query)
    return score_list(idea_query, patents, threshold)


def search_idea(idea_title="Tigers", idea_description="Lions and Bears", threshold=.5, max_depth=2,
                passed_types=['patent_type', 'google_type', 'youtube_type', 'scholar_type', ]):
    start = time.time()
    idea_query = query(idea_title, idea_description, [])
    ts = threaded_search(idea_query, threshold, passed_types)
    if len(ts) >= 1:
        print('Time : ', time.time() - start)

        return ts
    return [[query("No Ideas Match!", "", []), 0]]


def linear_search(idea_query, threshold):
    searched_results = searcher(idea_query)
    searched_patents = searcher_patent(idea_query, threshold)
    searched_ideas = score_list(iq=idea_query, queries_list=searched_results, threshold=threshold) + searched_patents

    return sorted(searched_ideas, key=lambda x: 1 / x[1])


def threaded_search(idea_query, threshold, passed_types):
    if len(passed_types)<1:
        return [[query("Error with filters", "Not Enough Filtrs", []), 0]]

    exec = ThreadPoolExecutor(4)

    algo_list = {'patent_type':get_patent_query, 'google_type':get_google_query , 'scholar_type':get_scholar_query, 'youtube_type':get_youtube_query}

    futures = []
    searched_ideas = []
    for pt in passed_types:
        future = exec.submit(score_query, algo_list[pt], idea_query, threshold)
        future.add_done_callback(custom_callback)
        futures.append(future)
    start = time.time()
    done, not_done = wait(futures, return_when=ALL_COMPLETED)
    for f in futures:
        searched_ideas += f.result()
    return sorted(searched_ideas, key=lambda x: 1 / x[1])


def custom_callback(fn):
    if fn.cancelled():
        print(f'{fn.arg}: canceled')
        return 'canceled'
    elif fn.done():
        error = fn.exception()
        if error:
            print(f'task: error returned: {error}')
            fn.result()
            return 'error'
        else:
            result = fn.result()

            print(f'task - {result} is done')
            return 'completed'
    return 'running'

