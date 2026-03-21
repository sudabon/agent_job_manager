"""Worker entrypoint."""

from arq import run_worker

from src.infra.queue.worker import WorkerSettings

if __name__ == "__main__":
    run_worker(WorkerSettings)  # type: ignore[arg-type]
