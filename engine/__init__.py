"""HRL X Antigravity Autonomous Goal Engine package."""

from .feudal_controller import (
    FeudalController,
    Subgoal,
    TaskDAG,
    OptionState,
    ActionVolatility,
)
from .verification_oracle import VerificationOracleSuite, OracleResult
from .state_compressor import StateCompressor, StateDifferential
from .notification_trigger import NotificationTrigger

__all__ = [
    "FeudalController",
    "Subgoal",
    "TaskDAG",
    "OptionState",
    "ActionVolatility",
    "VerificationOracleSuite",
    "OracleResult",
    "StateCompressor",
    "StateDifferential",
    "NotificationTrigger",
]
__version__ = "2.2.0"
