"""硬件无关的 V1 对局协调器。

识别器、规则引擎、AI、语音和传输层都通过小接口接入；真实实现可在后续替换。
"""

from dataclasses import dataclass
from typing import Optional
from .models import BoardSnapshot


class RuleEngine:
    def apply_observation(self, snapshot: BoardSnapshot) -> None: ...
    def is_legal_ai_move(self, uci_move: str) -> bool: ...


class ChessAI:
    def choose_move(self, snapshot: BoardSnapshot, difficulty: str) -> str: ...


class VoiceOutput:
    def speak_move(self, uci_move: str) -> None: ...
    def speak_error(self, message: str) -> None: ...


@dataclass
class ControllerResult:
    status: str
    move: Optional[str] = None
    error: Optional[str] = None


class ChessController:
    def __init__(self, rules: RuleEngine, ai: ChessAI, voice: VoiceOutput):
        self.rules = rules
        self.ai = ai
        self.voice = voice
        self.last_state_version = -1

    def on_stable_snapshot(self, snapshot: BoardSnapshot, difficulty: str = "basic") -> ControllerResult:
        try:
            snapshot.validate()
            if snapshot.state_version <= self.last_state_version:
                return ControllerResult("IGNORED_STALE")
            self.rules.apply_observation(snapshot)
            move = self.ai.choose_move(snapshot, difficulty)
            if not self.rules.is_legal_ai_move(move):
                raise ValueError(f"AI returned illegal move: {move}")
            self.last_state_version = snapshot.state_version
            self.voice.speak_move(move)
            return ControllerResult("WAIT_PLAYER", move=move)
        except Exception as exc:
            self.voice.speak_error(str(exc))
            return ControllerResult("UNSTABLE", error=str(exc))
