import unittest

from software.controller.loop import ChessController
from software.controller.models import BoardSnapshot, PieceObservation


class FakeRules:
    def __init__(self):
        self.snapshots = []

    def apply_observation(self, snapshot):
        self.snapshots.append(snapshot)

    def is_legal_ai_move(self, uci_move):
        return uci_move == "g1f3"


class FakeAI:
    def choose_move(self, snapshot, difficulty):
        return "g1f3"


class FakeVoice:
    def __init__(self):
        self.moves = []
        self.errors = []

    def speak_move(self, uci_move):
        self.moves.append(uci_move)

    def speak_error(self, message):
        self.errors.append(message)


def snapshot(version=1):
    return BoardSnapshot.from_pieces(
        "wx-001",
        "game-1",
        version,
        [PieceObservation("p01", "white", "knight", "g1")],
    )


class ControllerTests(unittest.TestCase):
    def test_stable_snapshot_produces_voice_guidance(self):
        rules, ai, voice = FakeRules(), FakeAI(), FakeVoice()
        result = ChessController(rules, ai, voice).on_stable_snapshot(snapshot())
        self.assertEqual(result.status, "WAIT_PLAYER")
        self.assertEqual(result.move, "g1f3")
        self.assertEqual(voice.moves, ["g1f3"])

    def test_stale_snapshot_is_ignored(self):
        rules, ai, voice = FakeRules(), FakeAI(), FakeVoice()
        controller = ChessController(rules, ai, voice)
        controller.on_stable_snapshot(snapshot(2))
        result = controller.on_stable_snapshot(snapshot(2))
        self.assertEqual(result.status, "IGNORED_STALE")

    def test_duplicate_square_is_rejected(self):
        with self.assertRaises(ValueError):
            BoardSnapshot.from_pieces(
                "wx-001",
                "game-1",
                1,
                [
                    PieceObservation("p01", "white", "king", "e1"),
                    PieceObservation("p02", "black", "rook", "e1"),
                ],
            )


if __name__ == "__main__":
    unittest.main()

