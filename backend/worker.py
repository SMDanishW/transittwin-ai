import asyncio
import logging

from arq import run_worker

from app.workers.gtfs_rt_worker import WorkerSettings

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    asyncio.run(run_worker(WorkerSettings))
