"""
In-memory per-chat playback queue + play state.
(A dedicated Redis/Mongo-backed queue can replace this later without
touching the handler code — everything goes through the functions
below.)
"""

import random
from dataclasses import dataclass, field


@dataclass
class Track:
    title: str
    duration: str
    webpage_url: str
    file_path: str = ""
    requested_by: int = 0


@dataclass
class ChatState:
    queue: list[Track] = field(default_factory=list)
    repeat: bool = False
    is_playing: bool = False


_state: dict[int, ChatState] = {}


def get_state(chat_id: int) -> ChatState:
    if chat_id not in _state:
        _state[chat_id] = ChatState()
    return _state[chat_id]


def add_track(chat_id: int, track: Track):
    get_state(chat_id).queue.append(track)


def pop_next(chat_id: int) -> Track | None:
    state = get_state(chat_id)
    if not state.queue:
        return None
    track = state.queue.pop(0)
    if state.repeat:
        state.queue.insert(0, track)
    return track


def play_next_now(chat_id: int, track: Track):
    """Insert at position 0 so it plays immediately after current track."""
    get_state(chat_id).queue.insert(0, track)


def shuffle_queue(chat_id: int):
    random.shuffle(get_state(chat_id).queue)


def clear_queue(chat_id: int):
    get_state(chat_id).queue.clear()


def toggle_repeat(chat_id: int) -> bool:
    state = get_state(chat_id)
    state.repeat = not state.repeat
    return state.repeat
