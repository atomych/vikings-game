from enum import Enum
from typing import Dict, List, Callable, Set, Any

from game_objects.component import Component


class EventType(Enum):
    # ===== ДВИЖЕНИЕ И ФИЗИКА =====
    VELOCITY_CHANGED = "velocity_changed"
    COLLISION_STARTED = "collision_started"
    COLLISION_ENDED = "collision_ended"
    TRIGGER_ENTER = "trigger_enter"
    TRIGGER_EXIT = "trigger_exit"

    #ControllerComponent
    MOVEMENT_STATE_CHANGED = "movement_state_changed" #obj, new_state, old_state with reuse_cache
    MOVEMENT_STARTED = "player_pick_up_item"
    MOVEMENT_STOPPED = "movement_stopped"



class Event:
    __slots__ = ('type', '_args', '_kwargs', 'handled')  # Фиксированные атрибуты для скорости

    def __init__(self, event_type: Enum, *args, **kwargs):
        self.type = event_type
        self._args = args
        self._kwargs = kwargs
        self.handled = False

    @property
    def data(self):
        return self._args if len(self._args) != 1 else self._args[0]


class EventManager:
    def __init__(self):
        self.event_types: Set[Enum] = set()
        self.event_handlers: Dict[Enum, List[Callable]] = {}
        self._cached_events: Dict[Enum, Event] = {}
        self._init_event_types()

    def _init_event_types(self):
        for key in EventType:
            self.register_event_type(key)

    def register_event_type(self, event_type: Enum) -> None:
        """Зарегистрировать новый тип события для этого компонента"""
        self.event_types.add(event_type)
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []

    def on_event(self, event_type, callback: Callable):
        if event_type not in self.event_types:
            self.register_event_type(event_type)
        if callback not in self.event_handlers[event_type]:
            self.event_handlers[event_type].append(callback)
        return self

    def off_event(self, event_type, callback: Callable):
        """Отписаться от события"""
        if event_type in self.event_handlers:
            if callback in self.event_handlers[event_type]:
                self.event_handlers[event_type].remove(callback)

    def emit(self, event_type: Enum, *args, reuse_cache: bool = False, **kwargs) -> Event:
        if reuse_cache and event_type in self._cached_events:
            event = self._cached_events[event_type]
            event._kwargs = kwargs
            event.handled = False
        else:
            event = Event(event_type, *args, **kwargs)
            if reuse_cache:
                self._cached_events[event_type] = event

        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type][:]:  # Копируем для безопасности
                if event.handled:
                    break
                handler(event)
        return event


# глобальная переменная
event_manager = EventManager()
