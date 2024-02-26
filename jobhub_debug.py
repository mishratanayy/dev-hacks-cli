import sys
import time

from schrodinger.infra import jobhub


def get_subjobs(jobs):
    start = time.time()
    total_jobs = 0

    for job in jobs:
        subjobs = job.SubJobs
    
    print(f"Time taken to get subjobs of {len(jobs)} jobs is:",
          time.time() - start)
    print("total jobs via sub jobs", total_jobs)
    sys.exit(0)


def main():
    jm = jobhub.get_job_manager()
    jm.jobsChanged.connect(get_subjobs)


if __name__ == '__main__':
    from schrodinger.utils import qapplication
    qapplication.start_application(main)