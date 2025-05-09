from typing import Any, Optional, Protocol

from rich.progress import Progress


class Progressbar(Protocol):
    """Progressbar protocol modeled after tqdm"""

    total: Optional[int]

    def update(self, increment: int, /) -> Any: ...

    def reset(self): ...

    def close(self): ...

    def set_description(self, description: str, /, refresh: bool = True): ...


class RichTaskBar:
    def __init__(self, description: str, *, parent: Progress, total: Optional[int]):
        super().__init__()
        self.task_id = parent.add_task(description, total=total)
        self.parent = parent
        self.total = total

    def update(self, increment: int, /):
        self.parent.advance(self.task_id, increment)

    def reset(self):
        self.parent.reset(self.task_id)

    def close(self):
        self.parent.remove_task(self.task_id)

    def set_description(self, description: str, /, refresh: bool = True):
        self.parent.update(self.task_id, description=description, refresh=refresh)


class RichOverallProgress:
    def __init__(self):
        super().__init__()
        self.progress = Progress()

    def __call__(self, description: str = "", *, total: Optional[int] = None):
        return RichTaskBar(description, parent=self.progress, total=total)
