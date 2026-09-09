"""
五子棋游戏主程序
人机对战 / 双人对战
"""

import argparse
import sys
from .board import GomokuBoard, BLACK, WHITE
from .ai import GomokuAI


class GomokuGame:
    def __init__(self, size=15, difficulty='medium', human_player=BLACK):
        self.board = GomokuBoard(size)
        self.ai = GomokuAI(difficulty)
        self.ai.set_ai_player(WHITE if human_player == BLACK else BLACK)
        self.human_player = human_player
        
    def play_human_move(self, row, col):
        """人类落子"""
        if self.board.current_player != self.human_player:
            return False, "还没轮到你"
        if not self.board.make_move(row, col):
            return False, "非法落子"
        return True, ""
    
    def play_ai_move(self):
        """AI落子，返回(row, col)"""
        if self.board.current_player != self.ai.ai_player:
            return None
        move = self.ai.find_best_move(self.board)
        if move:
            self.board.make_move(move[0], move[1])
        return move
    
    def is_game_over(self):
        return self.board.is_game_over()
    
    def get_winner(self):
        return self.board.get_winner()
    
    def get_status(self):
        """获取游戏状态文本"""
        if self.board.winner:
            winner = "黑棋" if self.board.winner == BLACK else "白棋"
            return f"游戏结束，{winner}获胜！"
        if self.board.is_full():
            return "平局！"
        player = "黑棋" if self.board.current_player == BLACK else "白棋"
        return f"轮到{player}落子"


def main():
    parser = argparse.ArgumentParser(description="五子棋游戏")
    parser.add_argument("--size", type=int, default=15, help="棋盘大小")
    parser.add_argument("--difficulty", choices=['easy', 'medium', 'hard'], default='medium')
    parser.add_argument("--pvp", action="store_true", help="双人对战模式")
    args = parser.parse_args()
    
    game = GomokuGame(size=args.size, difficulty=args.difficulty)
    
    print("=== 五子棋 ===")
    print("输入格式: row col (例如: 7 7)")
    print("输入 'q' 退出\n")
    
    while not game.is_game_over():
        print(game.board)
        print(game.get_status())
        
        if args.pvp or game.board.current_player == game.human_player:
            # 人类回合
            try:
                user_input = input("你的落子: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n游戏退出")
                break
            
            if user_input.lower() == 'q':
                break
            
            try:
                row, col = map(int, user_input.split())
            except ValueError:
                print("输入格式错误，请输入: row col")
                continue
            
            success, msg = game.play_human_move(row, col)
            if not success:
                print(msg)
                continue
        else:
            # AI回合
            print("AI思考中...")
            move = game.play_ai_move()
            if move:
                print(f"AI落子: {move[0]} {move[1]}")
    
    print("\n" + "=" * 30)
    print(game.board)
    print(game.get_status())


if __name__ == "__main__":
    main()
