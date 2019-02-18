import time
from rq import get_current_job
import requests


def example(seconds):
    job = get_current_job()
    print('Starting task')
    for i in range(seconds):
        job.meta['progress'] = 100.0 * i / seconds
        job.save_meta()
        print(i)
        time.sleep(1)
    job.meta['progress'] = 100
    job.save_meta()
    print('Task completed')


def background_job():
    a = 1
    b = 1
    return a + b


def count_words_at_url(url):
    resp = requests.get(url)
    return len(resp.text.split())
