from types import TracebackType
from typing import Dict, List, Optional

class File:
    tags: Dict[str, List[str]]
    def __init__(self, file_name: str): ...
    def __enter__(self) -> File: ...
    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
    ) -> None: ...
