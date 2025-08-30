from typing import Callable, Optional, Dict, Any

PAGE_SIZE_DEFAULT = 200
MAX_WORKERS_DEFAULT = 6
SECOND_PASSES = 2
UPSERT_ATTEMPTS = 4
PROGRESS_EVERY_N = 10

ProgressState = Dict[str, Any]
ProgressFn = Optional[Callable[[ProgressState], None]]
LogFn = Optional[Callable[[str], None]]