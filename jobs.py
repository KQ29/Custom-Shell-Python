# jobs.py

import threading
from constants import RED, RESET

jobs_list = []
job_counter = 1

class Job:
    def __init__(self, job_id, thread, command):
        self.job_id = job_id
        self.thread = thread
        self.command = command

def add_job(thread, command):
    global job_counter
    job = Job(job_counter, thread, command)
    jobs_list.append(job)
    job_counter += 1
    print(f"[{job.job_id}] {thread.ident} Started '{command}'")
    return job.job_id

def list_jobs():
    for job in jobs_list:
        status = 'Running' if job.thread.is_alive() else 'Done'
        print(f"[{job.job_id}] {status} {job.command}")

def bring_job_to_foreground(job_id):
    for job in jobs_list:
        if job.job_id == job_id:
            job.thread.join()
            jobs_list.remove(job)
            print(f"Brought job [{job_id}] to foreground")
            return
    print(f"{RED}fg: No such job: {job_id}{RESET}")
