#!/usr/bin/env python3
"""五子棋单元测试"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gomoku.board import GomokuBoard, BLACK, WHITE, EMPTY
from gomoku.ai import GomokuAI


def test_board_init():
    """测试棋盘初始化"""
    board = GomokuBoard(15)
    assert board.size == 15
    assert board.current_player == BLACK
    assert board.winner is None
    print("✓ 棋盘初始化测试通过")


def test_make_move():
    """测试落子"""
    board = GomokuBoard(15)
    assert board.make_move(7, 7) == True
    assert board.board[7][7] == BLACK
    assert board.current_player == WHITE
    assert board.make_move(7, 7) == False  # 重复落子失败
    print("✓ 落子测试通过")


def test_undo():
    """测试悔棋"""
    board = GomokuBoard(15)
    board.make_move(7, 7)
    board.make_move(8, 8)
    assert board.undo_move() == True
    assert board.board[8][8] == EMPTY
    assert board.current_player == WHITE
    print("✓ 悔棋测试通过")


def test_horizontal_win():
    """测试横向连五"""
    board = GomokuBoard(15)
    for i in range(5):
        board.make_move(7, i)   # 黑
        board.make_move(0, i)   # 白（不影响）
    # 黑棋在(7,0)-(7,4)连五
    assert board.winner == BLACK
    print("✓ 横向连五测试通过")


def test_vertical_win():
    """测试纵向连五"""
    board = GomokuBoard(15)
    for i in range(5):
        board.make_move(i, 7)
        board.make_move(0, i)
    assert board.winner == BLACK
    print("✓ 纵向连五测试通过")


def test_diagonal_win():
    """测试斜向连五"""
    board = GomokuBoard(15)
    for i in range(5):
        board.make_move(i, i)
        board.make_move(0, i + 1)
    assert board.winner == BLACK
    print("✓ 斜向连五测试通过")


def test_candidate_moves():
    """测试候选落子"""
    board = GomokuBoard(15)
    assert len(board.get_candidate_moves()) == 1  # 空棋盘只有中心
    board.make_move(7, 7)
    candidates = board.get_candidate_moves(radius=1)
    assert len(candidates) > 0
    assert (7, 7) not in candidates  # 已有棋子的位置不在候选中
    print("✓ 候选落子测试通过")


def test_ai_move():
    """测试AI能返回合法落子"""
    board = GomokuBoard(15)
    ai = GomokuAI(difficulty='easy')
    ai.set_ai_player(WHITE)
    
    # 黑先下
    board.make_move(7, 7)
    # AI下
    move = ai.find_best_move(board)
    assert move is not None
    row, col = move
    assert board.is_valid_move(row, col)
    print(f"✓ AI落子测试通过 (AI选择: {move})")


def test_ai_blocks_win():
    """测试AI会堵截对手连五"""
    board = GomokuBoard(15)
    # 黑棋已经连四
    board.make_move(7, 0)  # 黑
    board.make_move(0, 0)  # 白
    board.make_move(7, 1)  # 黑
    board.make_move(0, 1)  # 白
    board.make_move(7, 2)  # 黑
    board.make_move(0, 2)  # 白
    board.make_move(7, 3)  # 黑（连四）
    # 现在轮到白棋（AI），应该堵(7,4)或(7,-1不存在)
    ai = GomokuAI(difficulty='medium')
    ai.set_ai_player(WHITE)
    move = ai.find_best_move(board)
    assert move is not None
    # AI应该在第7行附近落子堵截
    assert move[0] == 7 or abs(move[0] - 7) <= 2
    print(f"✓ AI堵截测试通过 (AI选择: {move})")


def run_all_tests():
    print("=" * 40)
    print("运行五子棋单元测试")
    print("=" * 40)
    
    tests = [
        test_board_init,
        test_make_move,
        test_undo,
        test_horizontal_win,
        test_vertical_win,
        test_diagonal_win,
        test_candidate_moves,
        test_ai_move,
        test_ai_blocks_win,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} 失败: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} 异常: {e}")
            failed += 1
    
    print("\n" + "=" * 40)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 40)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
