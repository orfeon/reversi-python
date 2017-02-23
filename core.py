import copy


class Board(object):

    __INDEXS = [i for i in range(0,64)]
    __INDEX_DIRS = [-9,-8,-7,-1,1,7,8,9]
    __INIT_STONES = [1 if i in [27,36] else -1 if i in [28,35] else 0 for i in range(0,64)]


    def __init__(self, stones=[]):
        self.__stones = stones if stones else self.__INIT_STONES
        self.__history = []

    @property
    def stones(self):
        return self.__stones

    def move(self, pos, stone):
        acquirable_indexs = self._calc_acquirable_indexs(pos, stone)
        if not acquirable_indexs:
            return 0

        for index in acquirable_indexs:
            self.__stones[index] = stone
        self.__stones[pos] = stone
        self.__history.append((pos, acquirable_indexs))
        return len(acquirable_indexs) + 1

    def skip(self):
        self.__history.append((-1, []))
        return 0

    def undo(self):
        if not self.__history:
            return
        pos, acquired_indexs = self.__history.pop()
        if pos < 0:
            return
        stone = self.__stones[pos]
        for index in acquired_indexs:
            self.__stones[index] = -stone
        self.__stones[pos] = 0

    def check_gameover(self):
        if self.count_stones() == 64:
            return True
        if len(self.__history) < 2:
            return False
        if self.__history[-1][0] < 0 and self.__history[-2][0] < 0:
            return True
        return False

    def calc_movable_pos(self, stone):
        movable_pos_list = []
        for pos in self.__INDEXS:
            acquirable_indexs = self._calc_acquirable_indexs(pos, stone)
            if len(acquirable_indexs) > 0:
                movable_pos_list.append(pos)
        return movable_pos_list

    def clear(self):
        self.__stones = list(self.__INIT_STONES)
        self.__history = []

    def get_turn(self):
        if not self.__history:
            return -1

        pos = self.__history[-1][0]
        if pos >= 0:
            return -self.__stones[pos]

        pos = self.__history[-2][0]
        if pos >= 0:
            return self.__stones[pos]

        return 0

    def count_move(self):
        return len(self.__history)

    def count_stones(self):
        return len([1 for i in self.__stones if i != 0])


    def _calc_acquirable_indexs(self, pos, stone):

        acquirable_indexs = []
        if self.__stones[pos] != 0 or pos < 0:
            return acquirable_indexs

        for index_dir in self.__INDEX_DIRS:
            pro_acquirable_indexs = []
            pre_x = pos % 8
            pre_y = pos / 8
            for index in self.__INDEXS[pos + index_dir::index_dir]:
                cur_x = index % 8
                cur_y = index / 8
                if abs(cur_x - pre_x) > 1 or abs(cur_y - pre_y) > 1:
                    break
                pre_x = cur_x
                pre_y = cur_y

                if self.__stones[index] == -stone:
                    pro_acquirable_indexs.append(index)
                else:
                    if self.__stones[index] == stone and len(pro_acquirable_indexs) > 0:
                        acquirable_indexs.extend(pro_acquirable_indexs)
                    break

        return acquirable_indexs


class Player(object):

    def __init__(self, evaluator, depth=4):
        self.__evaluator = evaluator
        self.__depth = depth
        self.__pos = -1

    def move(self, board, stone):

        movable_pos_list = board.calc_movable_pos(stone)
        if not movable_pos_list:
            board.skip()
            return -1
        elif len(movable_pos_list) == 1:
            pos = movable_pos_list[0]
            board.move(pos, stone)
            return pos

        ms, pos = self._alphabeta(copy.deepcopy(board), stone, -10000, 10000)
        board.move(pos, stone)
        print("COM hit pos: {0}, score: {1}".format(pos, ms))

        return pos

    def _alphabeta(self, board, stone, alpha, beta, depth=0):

        depth_th = self.__depth if board.count_stones() < 55 else 7

        if depth >= depth_th or board.check_gameover():
            if board.count_stones() < 55:
                return self.__evaluator.evaluate(board, stone), -1
            else:
                return self.__evaluator.evaluate_stone(board, stone), -1

        score_max = alpha
        pos_max = -1
        movable_pos_list = board.calc_movable_pos(stone)

        if not movable_pos_list:
            board.skip()
            score, _ = self._alphabeta(board, -stone, -beta, -score_max, depth + 1)
            score = -score
            board.undo()
            return score, -1

        for pos in movable_pos_list:
            board.move(pos, stone)
            score, _ = self._alphabeta(board, -stone, -beta, -score_max, depth + 1)
            score = -score
            board.undo()

            if score > score_max:
                score_max = score
                pos_max = pos

            if score_max >= beta:
                break

        return score_max, pos_max


class Evaluator(object):

    def __init__(self):
        pass

    def evaluate_stone(self, board, stone):
        mystones = len([1 for i in board.stones if i == stone])
        emstones = len([1 for i in board.stones if i == -stone])
        return mystones - emstones

    def evaluate(self, board, stone):

        ## stone count score
        mystones = len([1 for i in board.stones if i == stone])
        emstones = len([1 for i in board.stones if i == -stone])
        stone_count = mystones - emstones

        ## freeness score
        myposlist = board.calc_movable_pos(stone)
        emposlist = board.calc_movable_pos(-stone)
        pos_count = len(myposlist) - len(emposlist)

        ## fixed stones score
        def _calc_fixed_stone(stn, fixed_stones, kado, diffx, diffy, x, y):

            if board.stones[kado] != stn:
                return

            fixed_stones.append(kado)

            x = x if x >= y else x + 1
            y = y if y >= x else y + 1

            for ix in xrange(1, x):
                index = kado + ix * diffx
                if board.stones[index] != stn:
                    break
                fixed_stones.append(index)
            for iy in xrange(1, y):
                index = kado + iy * diffy
                if board.stones[index] != stn:
                    break
                fixed_stones.append(index)

            if ix < 3 or iy < 3:
                return

            newkado = kado + diffx + diffy
            _calc_fixed_stone(stn, fixed_stones, newkado, diffx, diffy, ix-1, iy-1)

        def calc_fixed_stone(stn):
            fixed_stones = []
            for kado, diffx, diffy in [(0,1,8),(7,-1,8),(56,1,-8),(63,-1,-8)]:
                _calc_fixed_stone(stn, fixed_stones, kado, diffx, diffy, 8, 8)
            fixed_stones = set(fixed_stones)
            return fixed_stones

        myfixedstone = calc_fixed_stone(stone)
        emfixedstone = calc_fixed_stone(-stone)
        fixedstone_count = len(myfixedstone) - len(emfixedstone)

        return stone_count + 6*pos_count + 4*fixedstone_count
