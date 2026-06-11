import asyncio
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


class AnalysisHub:
    """In-memory pub/sub broadcasting analysis progress to WebSocket clients.

    Progress is published from worker threads, so broadcasting is marshalled
    back onto the event loop via ``call_soon_threadsafe``.
    """

    def __init__(self) -> None:
        self._loop: asyncio.AbstractEventLoop | None = None
        self._subscribers: dict[int, set[asyncio.Queue]] = {}
        self._state: dict[int, dict[str, Any]] = {}

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def bind_loop_from_running(self) -> None:
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:  # pragma: no cover - no running loop
            pass

    def subscribe(self, project_id: int) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.setdefault(project_id, set()).add(queue)
        return queue

    def unsubscribe(self, project_id: int, queue: asyncio.Queue) -> None:
        subs = self._subscribers.get(project_id)
        if subs:
            subs.discard(queue)
            if not subs:
                self._subscribers.pop(project_id, None)

    def snapshot(self, project_id: int) -> dict[str, Any]:
        return self._state.get(project_id, {"running": False, "categories": {}})

    def publish(self, project_id: int, event: dict[str, Any]) -> None:
        self._apply_state(project_id, event)
        for queue in list(self._subscribers.get(project_id, ())):
            self._deliver(queue, event)

    # --- internals -------------------------------------------------------

    def _apply_state(self, project_id: int, event: dict[str, Any]) -> None:
        state = self._state.setdefault(project_id, {"running": False, "categories": {}})
        etype = event.get("type")
        if etype == "start":
            state["running"] = True
        elif etype == "complete":
            state["running"] = False
        elif etype == "progress":
            state["categories"][event["category"]] = {
                "status": event.get("status", "running"),
                "count": event.get("count", 0),
            }

    def _deliver(self, queue: asyncio.Queue, event: dict[str, Any]) -> None:
        if self._loop is not None and self._loop.is_running():
            self._loop.call_soon_threadsafe(queue.put_nowait, event)
        else:  # pragma: no cover - synchronous fallback (tests)
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                pass


hub = AnalysisHub()
