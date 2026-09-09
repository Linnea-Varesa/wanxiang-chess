"""
五子棋AI - Minimax + α-β剪枝
基于棋型评估函数
"""

import numpy as np
from .board import GomokuBoard, BLACK, WHITE, EMPTY


class GomokuAI:
    # 棋型分值
    SCORES = {
        'FIVE': 100000,       # 连五
        'OPEN_FOUR': 10000,   # 活四
        'FOUR': 1000,         # 冲四
        'OPEN_THREE': 500,    # 活三
        'THREE': 100,         # 眠三
        'OPEN_TWO': 50,       # 活二
        'TWO': 10,            # 眠二
        'ONE': 1,             # 单子
    }
    
    def __init__(self, difficulty='medium'):
        """
        难度: easy(2层), medium(3层), hard(4层)
        """
        self.depth_map = {'easy': 2, 'medium': 3, 'hard': 4}
        self.depth = self.depth_map.get(difficulty, 3)
        self.ai_player = WHITE  # AI默认执白
        
    def set_ai_player(self, player):
        self.ai_player = player
    
    def find_best_move(self, board):
        """
        找到最佳落子位置
        返回: (row, col)
        """
        best_score = -float('inf')
        best_move = None
        
        candidates = board.get_candidate_moves(radius=2)
        # 按位置评分排序，优先搜索好位置（提高剪枝效率）
        candidates.sort(key=lambda pos: self._position_priority(board, pos[0], pos[1]), reverse=True)
        
        # 限制候选数量（提高速度）
        if len(candidates) > 20:
            candidates = candidates[:20]
        
        for row, col in candidates:
            board.make_move(row, col)
            score = -self._minimax(board, self.depth - 1, -float('inf'), float('inf'))
            board.undo_move()
            
            if score > best_score:
                best_score = score
                best_move = (row, col)
        
        return best_move
    
    def _minimax(self, board, depth, alpha, beta):
        """Minimax + α-β剪枝"""
        if depth == 0 or board.is_game_over():
            return self._evaluate(board)
        
        candidates = board.get_candidate_moves(radius=1)
        if not candidates:
            return self._evaluate(board)
        
        # 排序提高剪枝效率
        candidates.sort(key=lambda pos: self._position_priority(board, pos[0], pos[1]), reverse=True)
        if len(candidates) > 10:
            candidates = candidates[:10]
        
        max_score = -float('inf')
        for row, col in candidates:
            board.make_move(row, col)
            score = -self._minimax(board, depth - 1, -beta, -alpha)
            board.undo_move()
            
            if score > max_score:
                max_score = score
            if score > alpha:
                alpha = score
            if alpha >= beta:
                break
        
        return max_score
    
    def _evaluate(self, board):
        """
        评估当前局面（从当前玩家视角）
        正值对当前玩家有利
        """
        current = board.current_player
        opponent = WHITE if current == BLACK else BLACK
        
        my_score = self._evaluate_player(board, current)
        opp_score = self._evaluate_player(board, opponent)
        
        # 防守权重略高于进攻（避免被连五）
        return my_score - opp_score * 1.1
    
    def _evaluate_player(self, board, player):
        """评估某玩家的总分"""
        total = 0
        size = board.size
        b = board.board
        
        # 四个方向：横、竖、斜、反斜
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for r in range(size):
            for c in range(size):
                if b[r][c] != player:
                    continue
                for dr, dc in directions:
                    # 只从每条线的起点开始统计（避免重复）
                    pr, pc = r - dr, c - dc
                    if 0 <= pr < size and 0 <= pc < size and b[pr][pc] == player:
                        continue
                    
                    # 统计连续棋子数和两端开放情况
                    count = 0
                    cr, cc = r, c
                    while 0 <= cr < size and 0 <= cc < size and b[cr][cc] == player:
                        count += 1
                        cr += dr
                        cc += dc
                    
                    # 检查两端
                    left_open = self._is_open(board, r - dr, c - dc)
                    right_open = self._is_open(board, cr, cc)
                    
                    total += self._pattern_score(count, left_open, right_open)
        
        return total
    
    def _is_open(self, board, r, c):
        """检查位置是否为空（可落子）"""
        if r < 0 or r >= board.size or c < 0 or c >= board.size:
            return False
        return board.board[r][c] == EMPTY
    
    def _pattern_score(self, count, left_open, right_open):
        """根据连子数和开放情况给分"""
        if count >= 5:
            return self.SCORES['FIVE']
        
        open_ends = int(left_open) + int(right_open)
        
        if count == 4:
            if open_ends == 2:
                return self.SCORES['OPEN_FOUR']
            elif open_ends == 1:
                return self.SCORES['FOUR']
        elif count == 3:
            if open_ends == 2:
                return self.SCORES['OPEN_THREE']
            elif open_ends == 1:
                return self.SCORES['THREE']
        elif count == 2:
            if open_ends == 2:
                return self.SCORES['OPEN_TWO']
            elif open_ends == 1:
                return self.SCORES['TWO']
        elif count == 1:
            if open_ends == 2:
                return self.SCORES['ONE']
        
        return 0
    
    def _position_priority(self, board, row, col):
        """位置优先级（用于排序，中心位置优先）"""
        center = board.size // 2
        dist = abs(row - center) + abs(col - center)
        return -dist  # 距离中心越近优先级越高
