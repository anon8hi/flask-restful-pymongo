import requests
from datetime import datetime
import threading
import sys


def update_db_frequently(thread_stop):
    '''using threading for periodical/frequent update of DB, with new jobs feed'''

    if not thread_stop.is_set():
        requests.post('http://127.0.0.1:5000/pull_jobs')
        print(
            datetime.now().strftime("%H:%M:%S"),
            ' - pulling RSS into DB ...')
        threading.Timer(15, update_db_frequently, [thread_stop]).start()


thread_stop = threading.Event()


if len(sys.argv) > 1:
    command = sys.argv[1]
    if command == 'home':
        respone = requests.get('http://127.0.0.1:5000/')
        print(respone.json())
    elif command == 'pull_jobs':
        respone = requests.post('http://127.0.0.1:5000/pull_jobs')
        print(respone.json())
    elif command == 'show_jobs':
        respone = requests.get('http://127.0.0.1:5000/show_jobs')
        print(respone.json())
    elif command == 'loop':
        update_db_frequently(thread_stop)
    else:
        print('Error: Unknown argument was passed to tryful.py')
else:
    respone = requests.get('http://127.0.0.1:5000/')
    print(respone.json())
