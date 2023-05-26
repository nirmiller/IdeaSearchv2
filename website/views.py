import threading
import time
from flask import jsonify, Blueprint, render_template, request, flash, session, redirect, url_for
from flask.cli import with_appcontext
import json
from ideasearch import ideasearcher
from concurrent.futures import ThreadPoolExecutor
from ideasearch.utils import query

views = Blueprint('views', __name__)
executor = ThreadPoolExecutor(2)


def get_meta(tag, data):
    if tag == 'PATENT':
        return f"Patent Number : {data[1]} \n Patent Date : {data[2]}"
    elif tag == 'GOOGLE_WEBSITE':
        return f"Website Link : {data[1]}"
    elif tag == 'YOUTUBE':
        return f'Youtube Link : {data[1]}'
    elif tag == 'SCHOLAR':
        return f'Paper Link : {data[1]} \n Paper ID : {data[2]}'


def find_icon(tag):
    if tag == 'PATENT':
        return url_for('static', filename='images/PatentIcon2.svg')
    elif tag == 'GOOGLE_WEBSITE':
        return url_for('static', filename='images/GoogleIcon.svg')
    elif tag == 'YOUTUBE':
        return url_for('static', filename='images/YoutubeIcon1.svg')
    elif tag == 'SCHOLAR':
        return url_for('static', filename='images/ScholarIcon.svg')


def execute_heavy_job(passed_types):
    global future

    it = session.get('idea_title')
    id = session.get('idea_desc')

    future = executor.submit(ideasearcher.search_idea, it, id, 0.25, 2, passed_types)
    future.add_done_callback(custom_callback)
    return 'Heavy job started. Result will be available soon.'


@views.route('/idea', methods=['GET', 'POST'])
def idea():
    if request.method == 'POST':
        index = request.form.get('index')
        current_res = future.result()[int(index)]
        print(current_res)
        return render_template('idea.html', result=current_res, find_icon=find_icon, get_meta=get_meta)
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
        idea_title = request.form.get('idea_title')
        idea_desc = request.form.get('idea_desc')

        passed_types = request.form.getlist('search_types')

        session['idea_title'] = idea_title
        session['idea_desc'] = idea_desc

        execute_heavy_job(passed_types)

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
        sum = 0
        for i in range(len(r)):
            sum += (1 - r[i][1]) * 100
        s = round(sum / len(r), 2)

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
