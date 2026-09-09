#!/usr/bin/env python3
"""
国际象棋集成模块
使用 python-chess 处理规则，Stockfish 作为AI引擎
"""

import chess
import os
import sys


class ChessIntegration:
    def __init__(self, stockfish_path=None):
        """
        初始化国际象棋模块
        stockfish_path: Stockfish引擎路径，为None则自动查找
        """
        self.board = chess.Board()
        self.engine = None
        self.stockfish_path = stockfish_path or self._find_stockfish()
        
    def _find_stockfish(self):
        """自动查找Stockfish引擎"""
        candidates = [
            '/usr/games/stockfish',
            '/usr/local/bin/stockfish',
            '/opt/homebrew/bin/stockfish',  # Mac M系列
            '/usr/bin/stockfish',
            'stockfish',  # PATH中查找
        ]
        for path in candidates:
            if os.path.exists(path) or path == 'stockfish':
                return path
        return None
    
    def start_engine(self):
        """启动Stockfish引擎"""
        if self.stockfish_path is None:
            print("[Chess] 警告: 未找到Stockfish引擎，AI功能不可用")
            print("  安装方法: sudo apt install stockfish (Linux)")
            print("           brew install stockfish (Mac)")
            print("           下载: https://stockfishchess.org/download/ (Windows)")
            return False
        
        try:
            import chess.engine
            self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
            print("[Chess] Stockfish引擎已启动")
            return True
        except Exception as e:
            print(f"[Chess] 启动引擎失败: {e}")
            return False
    
    def stop_engine(self):
        """关闭引擎"""
        if self.engine:
            self.engine.quit()
            self.engine = None
    
    def reset(self):
        """重置棋盘"""
        self.board = chess.Board()
    
    def make_move(self, move_str):
        """
        执行一步棋（标准代数记谱，如 'e4', 'Nf3'）
        返回: (成功, 消息)
        """
        try:
            move = self.board.push_san(move_str)
            return True, str(move)
        except ValueError:
            return False, "非法走法"
    
    def make_move_uci(self, uci_str):
        """
        执行一步棋（UCI格式，如 'e2e4'）
        """
        try:
            move = chess.Move.from_uci(uci_str)
            if move in self.board.legal_moves:
                self.board.push(move)
                return True, str(move)
            return False, "非法走法"
        except ValueError:
            return False, "格式错误"
    
    def get_ai_move(self, time_limit=0.5):
        """
        获取AI走法
        返回: UCI格式的走法字符串，如 'e2e4'
        """
        if self.engine is None:
            # 无引擎时使用简单策略
            return self._simple_ai_move()
        
        try:
            result = self.engine.play(self.board, chess.engine.Limit(time=time_limit))
            if result.move:
                return result.move.uci()
        except Exception as e:
            print(f"[Chess] AI计算失败: {e}")
        
        return None
    
    def _simple_ai_move(self):
        """无Stockfish时的简单AI（随机选择合法走法）"""
        import random
        moves = list(self.board.legal_moves)
        if moves:
            return random.choice(moves).uci()
        return None
    
    def get_legal_moves(self):
        """获取所有合法走法（UCI格式列表）"""
        return [move.uci() for move in self.board.legal_moves]
    
    def is_game_over(self):
        return self.board.is_game_over()
    
    def get_result(self):
        """获取游戏结果"""
        if self.board.is_checkmate():
            winner = "白方" if self.board.turn == chess.BLACK else "黑方"
            return f"将死！{winner}获胜"
        if self.board.is_stalemate():
            return "逼和（平局）"
        if self.board.is_insufficient_material():
            return "子力不足（平局）"
        if self.board.is_seventyfive_moves():
            return "75回合规则（平局）"
        if self.board.is_fivefold_repetition():
            return "五次重复（平局）"
        return "游戏进行中"
    
    def get_board_fen(self):
        """获取FEN字符串（用于保存/传输）"""
        return self.board.fen()
    
    def load_fen(self, fen):
        """从FEN加载棋盘"""
        try:
            self.board = chess.Board(fen)
            return True
        except ValueError:
            return False
    
    def square_to_grid(self, square):
        """
        将棋盘方格转换为(row, col)坐标
        a1 -> (7, 0), h8 -> (0, 7)
        """
        row = 7 - chess.square_rank(square)
        col = chess.square_file(square)
        return row, col
    
    def move_to_grids(self, uci_move):
        """
        将UCI走法转换为起点和终点的(row, col)坐标
        'e2e4' -> ((6, 4), (4, 4))
        """
        move = chess.Move.from_uci(uci_move)
        from_sq = self.square_to_grid(move.from_square)
        to_sq = self.square_to_grid(move.to_square)
        return from_sq, to_sq
    
    def __str__(self):
        return str(self.board)


def main():
    """命令行测试"""
    chess_game = ChessIntegration()
    chess_game.start_engine()
    
    print("=== 国际象棋 ===")
    print("输入走法 (如 e4, Nf3)，输入 'ai' 让AI走，输入 'q' 退出\n")
    
    while not chess_game.is_game_over():
        print(chess_game.board)
        print(f"轮到: {'白方' if chess_game.board.turn == chess.WHITE else '黑方'}")
        
        try:
            user_input = input("走法: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        
        if user_input.lower() == 'q':
            break
        elif user_input.lower() == 'ai':
            move = chess_game.get_ai_move()
            if move:
                chess_game.make_move_uci(move)
                print(f"AI走: {move}")
            continue
        
        success, msg = chess_game.make_move(user_input)
        if not success:
            print(msg)
    
    print("\n" + chess_game.get_result())
    chess_game.stop_engine()


if __name__ == "__main__":
    main()
