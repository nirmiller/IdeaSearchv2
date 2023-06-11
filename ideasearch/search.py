import requests
from .variables import GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_ID, header, youtube, patent_header
from .utils import query


def get_scholar_query(search, depth=False):
    scholar_depth = 10
    if depth:
        scholar_depth = 25

    scholar_query_resuts = []
    print("Scholar", search.title)
    try:
        r = requests.get(
            f'http://api.semanticscholar.org/graph/v1/paper/search?query={search.title}&offset=10&limit={scholar_depth}&fields=title,authors,url,abstract')
        data = r.json()
        print(data)
        for d in data['data']:
            scholar_query_resuts.append(query(d['title'], d['abstract'], ['SCHOLAR', d['url'], d['paperId']]))
    except Exception as e:
        print("Error with scholar api", e)
        return scholar_query_resuts
    print('Scholar Search Length', len(scholar_query_resuts))
    return scholar_query_resuts


def get_youtube_query(search, depth=False):

    youtube_search_depth = 10
    if depth:
        youtube_search_depth = 100

    youtube_query_resuts = []
    print("YOUTUBE", search.title)
    try:
        request = youtube.search().list(q=search.title, part='snippet', type='video', maxResults=youtube_search_depth, order='viewCount')
        res = request.execute()
        for item in res['items']:
            video_id = item['id']['videoId']
            link = f'https://www.youtube.com/watch?v={video_id}'
            youtube_query_resuts.append(query(item['snippet']['title'], "NA", ['YOUTUBE', link]))
    except Exception as e:
        print("Error with youtube api", e)
        return youtube_query_resuts
    print('Youtube Search Length', len(youtube_query_resuts))

    return youtube_query_resuts


def get_google_query(search, depth=False):
    google_search_depth = 10
    google_page_depth = 3
    if depth:
        google_search_depth = 1000
        google_page_depth = 100

    query_results = []

    for i in range(1, google_page_depth):
        try:
            page = i
            start = (page - 1) * 10 + 1

            url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_SEARCH_ENGINE_ID}&q={search.title}&start={start}"
            data = requests.get(url=url, headers=header).json()
            search_items = data.get("items")
            print('GOOGLE', search.title)
            for i, search_item in enumerate(search_items, start=1):
                try:
                    long_description = search_item["pagemap"]["metatags"][0]["og:description"]
                except Exception as e:
                    long_description = "NA"
                title = search_item.get("title")
                # print(search_item.get('link'))
                query_results.append(query(title, long_description, ['GOOGLE_WEBSITE', search_item['link']]))
        except Exception as e:
            print("Error with google api", e)

        return query_results

    return query_results


def get_patent_query(search, depth=False):
    if depth:

        patent_query_results = []
        query_url = ""
        print("Patent", search.title)
        try:
            if search.description == None or search.description == 'NA':
                query_url = 'https://api.patentsview.org/patents/query?o={{"size":10}}&q={{"_and":[{{"_gte":{{"patent_date":"2001-01-01"}}}},{{"_text_any":{{"patent_title":"{}"}}}}]}}&f=["patent_number","patent_title", "patent_abstract",  "patent_date"]'.format(
                    search.title)
            else:
                query_url = 'https://api.patentsview.org/patents/query?o={{"size":10}}&q={{"_and":[{{"_gte":{{"patent_date":"2001-01-01"}}}},{{"_text_any":{{"patent_title":"{}","patent_abstract":"{}"}}}}]}}&f=["patent_number","patent_title", "patent_abstract",  "patent_date"]'.format(
                    search.title, search.description)
            r = requests.get(query_url, headers=patent_header)
            data = r.json()

            print("Patent search length ", len(data['patents']))
            for d in data['patents']:
                patent_query_results.append(
                    query(d['patent_title'], d['patent_abstract'], ['PATENT', d['patent_number'], d['patent_date']]))
        except Exception as e:
            print("Error with patent api", e)
            return patent_query_results

        return patent_query_results
    return []


def searcher(search_query):
    search_web = []
    try:
        if len(search_query.title) < 70:
            search_web = get_google_query(search_query) + get_scholar_query(search_query) + get_youtube_query(
                search_query)
    except Exception as e:
        print(e)
        print("Error with searcher")
        return query("No Results", "404", [])

    return search_web
