import threading
import time
from flask import jsonify, Blueprint, render_template, request, flash, session, redirect, url_for
from flask.cli import with_appcontext
import json
from ideasearch import ideasearcher
from concurrent.futures import ThreadPoolExecutor
from ideasearch.utils import query
import json
import requests
from bs4 import BeautifulSoup

views = Blueprint('views', __name__)
executor = ThreadPoolExecutor(2)


def get_search_desc(idea):
    return idea


def get_search_title(idea):
    return idea


def get_meta(search_data):
    tag = search_data[0].data[0]
    url = search_data[0].data[1]
    image = None
    extra_data = []
    if tag == 'GOOGLE_WEBSITE' or tag == 'YOUTUBE':
        info = extract_info(url, tag)
        if info == -1:
            image = find_icon(tag)
        else:
            image = info['image_url']
        extra_data = []

    elif tag == 'SCHOLAR':
        extra_data = [f'Paper Link : {search_data[0].data[1]}', f'Paper ID : {search_data[0].data[2]}']
        image = find_icon(tag)
        url = ''
    elif tag == 'PATENT':
        extra_data = [f'Patent Number : {search_data[0].data[1]}', f'Patent Date : {search_data[0].data[2]}']
        image = find_icon(tag)
        url = ''

    return image, extra_data, url



def find_icon(tag):
    if tag == 'PATENT':
        return url_for('static', filename='images/PatentIcon2.svg')
    elif tag == 'GOOGLE_WEBSITE':
        return url_for('static', filename='images/GoogleIcon.svg')
    elif tag == 'YOUTUBE':
        return url_for('static', filename='images/YoutubeIcon1.svg')
    elif tag == 'SCHOLAR':
        return url_for('static', filename='images/ScholarIcon.svg')


def execute_heavy_job(search_depth):
    global future

    idea = session.get('idea')

    future = executor.submit(ideasearcher.search_idea, idea, 0.25, 2, search_depth)
    future.add_done_callback(custom_callback)
    return 'Heavy job started. Result will be available soon.'


@views.route('/idea', methods=['GET', 'POST'])
def idea():
    if request.method == 'POST':
        index = request.form.get('index')
        current_res = future.result()[int(index)]

        image_l, extra_d, url = get_meta(current_res)
        print('TYPE', current_res[0].data[0])
        return render_template('idea.html', result=current_res, find_icon=find_icon, image_link=image_l, extra_data=extra_d, url=url)
    return "<h1>Hello</h1>"


@views.route('/check_job')
def check_job():
    if future.done():
        return 'completed'
    else:
        return 'running'


@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        idea = request.form.get('idea')
        search_depth = False
        if request.form.get('search_depth') == 'on':
            search_depth = True
        else:
            search_depth = False

        session['idea'] = idea

        execute_heavy_job(search_depth)

        # Thread return progress through return of the function
        return redirect(url_for('views.loading'))

    return render_template('home.html')


@views.route('/loading')
def loading():
    return render_template('loading.html')


@views.route('/results', methods=['GET', 'POST'])
def results():
    if future.done():
        r = future.result()
        # session['results'] = jsonify(r)
        '''
        sum = 0
        for i in range(len(r)):
            sum += (1 - r[i][1]) * 100
        s = round(sum / len(r), 2)
        '''
        s = round(1 - r[0][1], 2) * 100
        return render_template('results.html', score=s, result=r, find_icon=find_icon, result_range=range(len(r)))
    else:
        return "The heavy job is still running. Please wait."


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


def extract_info(url, tag):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        default_image_url = find_icon(tag)

        # Extract title, description, and preview image
        title = soup.find('title').text
        description = soup.find('meta', {'name': 'description'})['content']

        # Check if the webpage has Open Graph metadata
        og_image = soup.find('meta', {'property': 'og:image'})
        if og_image:
            image_url = og_image['content']
        else:
            # If no Open Graph metadata is found, assign the default image URL
            image_url = default_image_url

        return {'url': url, 'title': title, 'description': description, 'image_url': image_url}
    except Exception as e:
        print('ERROR', e)
        return -1