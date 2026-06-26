import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any

logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=4)

_task_results: dict[str, Any] = {}


def run_background(task_id: str, func: Callable, *args, **kwargs) -> str:
    def _wrapper():
        try:
            result = func(*args, **kwargs)
            _task_results[task_id] = {"status": "completed", "result": result}
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            _task_results[task_id] = {"status": "failed", "error": str(e)}

    executor.submit(_wrapper)
    return task_id


def get_task_result(task_id: str) -> dict:
    return _task_results.get(task_id, {"status": "unknown"})
