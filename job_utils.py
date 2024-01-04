from schrodinger.infra import jobhub
from schrodinger.Qt import QtCore


class JobTracker:
    def __init__(self, job_id):
        self._job_id = job_id
        self._timer = QtCore.QElapsedTimer()
        self._timer.start()
        job_manager = jobhub.get_job_manager()
        print("Before starting job")
        self._printAllJobsCount()
        job_manager.jobCompleted.connect(self._onJobCompleted)
        job_manager.jobStarted.connect(self._onJobStarted)
        print(f"Timer started for job {job_id}")

    def _printAllJobsCount(self):
        job_manager = jobhub.get_job_manager()
        print(f"Job count: {len(job_manager.getJobs(jobhub.JobOption.ALL_JOBS))}")

    def _onJobCompleted(self, job):
        print("Inside Job completed")
        print(f"Job {job.job_id} completed in {self._timer.elapsed()} ms")
        self._printAllJobsCount()
        print("Exiting Job completed")

    def _onJobStarted(self, job):
        print("Inside Job started")
        self._printAllJobsCount()
        print(f"Job {job.job_id} started in {self._timer.elapsed()} ms")
        print("Exiting Job started")