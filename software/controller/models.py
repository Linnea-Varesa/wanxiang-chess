"""新方向的最小棋子和快照模型；不依赖硬件或第三方库。"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable, List, Set


FILES = "abcdefgh"


@dataclass(frozen=True)
class PieceObservation:
    uid: str
    side: str
    role: str
    square: str
    confidence: float = 1.0

    def validate(self) -> None:
        if self.side not in {"white", "black"}:
            raise ValueError(f"invalid side: {self.side}")
        if self.role not in {"king", "queen", "rook", "bishop", "knight", "pawn"}:
            raise ValueError(f"invalid role: {self.role}")
        if len(self.square) != 2 or self.square[0] not in FILES or self.square[1] not in "12345678":
            raise ValueError(f"invalid square: {self.square}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"invalid confidence: {self.confidence}")


@dataclass
class BoardSnapshot:
    device_id: str
    game_id: str
    state_version: int
    pieces: List[PieceObservation] = field(default_factory=list)
    observed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def validate(self, confidence_threshold: float = 0.9) -> None:
        if self.state_version < 0:
            raise ValueError("state_version must be non-negative")
        seen_uid: Set[str] = set()
        seen_square: Set[str] = set()
        for piece in self.pieces:
            piece.validate()
            if piece.uid in seen_uid:
                raise ValueError(f"duplicate uid: {piece.uid}")
            if piece.square in seen_square:
                raise ValueError(f"duplicate square: {piece.square}")
            if piece.confidence < confidence_threshold:
                raise ValueError(f"low confidence at {piece.square}")
            seen_uid.add(piece.uid)
            seen_square.add(piece.square)

    @classmethod
    def from_pieces(cls, device_id: str, game_id: str, state_version: int,
                    pieces: Iterable[PieceObservation]) -> "BoardSnapshot":
        snapshot = cls(device_id, game_id, state_version, list(pieces))
        snapshot.validate()
        return snapshot
