"""
五子棋棋盘规则引擎
支持15×15标准棋盘，可配置为其他尺寸
"""

import numpy as np

# 棋子类型
EMPTY = 0
BLACK = 1
WHITE = 2


class GomokuBoard:
    def __init__(self, size=15):
        self.size = size
        self.board = np.zeros((size, size), dtype=int)
        self.history = []  # 落子历史 [(row, col, player), ...]
        self.current_player = BLACK
        self.winner = None
        
    def reset(self):
        """重置棋盘"""
        self.board.fill(EMPTY)
        self.history.clear()
        self.current_player = BLACK
        self.winner = None
        
    def is_valid_move(self, row, col):
        """检查是否为合法落子"""
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return False
        return self.board[row][col] == EMPTY
    
    def make_move(self, row, col):
        """
        落子
        返回: True成功, False失败
        """
        if not self.is_valid_move(row, col) or self.winner is not None:
            return False
        
        self.board[row][col] = self.current_player
        self.history.append((row, col, self.current_player))
        
        # 检查胜负
        if self._check_win(row, col, self.current_player):
            self.winner = self.current_player
        else:
            self.current_player = WHITE if self.current_player == BLACK else BLACK
        
        return True
    
    def undo_move(self):
        """悔棋"""
        if not self.history:
            return False
        row, col, player = self.history.pop()
        self.board[row][col] = EMPTY
        self.current_player = player
        self.winner = None
        return True
    
    def _check_win(self, row, col, player):
        """检查在(row,col)落子后是否获胜"""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # 横、竖、斜、反斜
        
        for dr, dc in directions:
            count = 1
            # 正方向
            r, c = row + dr, col + dc
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc
            # 反方向
            r, c = row - dr, col - dc
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                count += 1
                r -= dr
                c -= dc
            
            if count >= 5:
                return True
        return False
    
    def get_candidate_moves(self, radius=2):
        """
        获取候选落子位置（已有棋子周围radius范围内的空位）
        用于AI搜索剪枝
        """
        if not self.history:
            # 空棋盘，下中心
            return [(self.size // 2, self.size // 2)]
        
        candidates = set()
        for row, col, _ in self.history:
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    r, c = row + dr, col + dc
                    if 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == EMPTY:
                        candidates.add((r, c))
        return list(candidates)
    
    def is_full(self):
        """棋盘是否已满"""
        return len(self.history) >= self.size * self.size
    
    def is_game_over(self):
        """游戏是否结束"""
        return self.winner is not None or self.is_full()
    
    def get_winner(self):
        """获取胜者"""
        return self.winner
    
    def copy(self):
        """深拷贝"""
        new_board = GomokuBoard(self.size)
        new_board.board = self.board.copy()
        new_board.history = self.history.copy()
        new_board.current_player = self.current_player
        new_board.winner = self.winner
        return new_board
    
    def __str__(self):
        """打印棋盘"""
        lines = []
        header = "   " + " ".join(f"{c:2d}" for c in range(self.size))
        lines.append(header)
        for r in range(self.size):
            row_str = f"{r:2d} "
            for c in range(self.size):
                piece = self.board[r][c]
                if piece == BLACK:
                    row_str += " ●"
                elif piece == WHITE:
                    row_str += " ○"
                else:
                    row_str += " ·"
            lines.append(row_str)
        return "\n".join(lines)
