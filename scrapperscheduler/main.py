import uuid
from datetime import datetime
from multiprocessing import Process
import time
import requests
import scrappers

running_jobs = []

USERNAME = 'admin'
PASSWORD = 'admin'


def run_task(task):
    runned_task_request = {
        'username': USERNAME,
        'password': PASSWORD,
        'requestType': 'updateExecutedTask',
        'requestData': {
            'owner_id': task['owner_id'],
            'id': str(uuid.uuid4()),
            'parent_planned_task_id': task['id'],
            'runStart': datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
            'status': 'running'
        }
    }

    requests.post(url='http://127.0.0.1:8000/executed_tasks/', json=runned_task_request)

    def scraped_offer_sender(offer_data):
        scraped_offer_request = {
            'username': USERNAME,
            'password': PASSWORD,
            'requestType': 'setNewScrappedOffer',
            'requestData': offer_data
        }

        scraped_offer_request['requestData']['task_run_id'] = runned_task_request['requestData']['id']
        scraped_offer_request['requestData']['owner_id'] = task['owner_id']

        requests.post(url='http://127.0.0.1:8000/scrapped_offers/', json=scraped_offer_request)
        print('done')

    scrappers.run_scraping_job(task, scraped_offer_sender)

    runned_task_request['requestData']['status'] = 'finished'
    requests.post(url='http://127.0.0.1:8000/executed_tasks/', json=runned_task_request)

    requests.post('http://127.0.0.1:8000/tasks/', json={
        'username': USERNAME,
        'password': PASSWORD,
        'requestType': 'updateTaskAfterRun',
        'requestData': {
            'id': task['id']
        }
    }).json()


def update_cycle():
    global running_jobs

    running_jobs = [job for job in running_jobs if job[1].is_alive()]
    ready_tasks = requests.post('http://127.0.0.1:8000/tasks/', json={
        'username': USERNAME,
        'password': PASSWORD,
        'requestType': 'getReadyTasks',
        'requestData': {}
    }).json()

    if 'log' in ready_tasks:
        print(ready_tasks['log'])
    else:
        for task in ready_tasks:
            if not task['id'] in [job[0] for job in running_jobs]:
                job = Process(target=run_task, args=(task,))
                job.start()
                running_jobs.append([task['id'], job])


if __name__ == "__main__":
    while True:
        try:
            update_cycle()
            time.sleep(60)
        except Exception as e:
            print(e)
