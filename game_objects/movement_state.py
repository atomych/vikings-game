from enum import Enum, auto


class MovementState(Enum):
    """Состояния движения персонажа"""
    IDLE    = "idle"
    WALK    = "walk"
    RUN     = "run"
    PICK_UP = "pick up"
    CROUCH  = "crouch"
    ATTACK  = "attack"