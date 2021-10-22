# -*- coding: utf-8 -*-

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum, auto

import numpy as np

from termcolors import TermColors


E, W, R, U, G, H, K, L, S, T, A, C, D, Y = EMPTY, WALL, ROCK, UNDEAD, GIRL, HELLTAKER, KEY, LOCK, SPIKES_UP, SPIKES_DOWN, \
                                  SPIKES_ALWAYS, CODE_UNDER_ROCK, CODE, KEY_UNDER_ROCK = range(14)
TO_STR = {E: '·', W: '█', R: 'R', U: 'U', G: 'G', H: 'H', K: 'K', L: 'L', C: 'C', D: 'D', Y: 'Y'}


class IllegalMove(ValueError):
    pass


@dataclass
class Position:
    row: int
    col: int

    def __str__(self):
        return f'({self.row}, {self.col})'

    def __add__(self, other):
        return Position(self.row + other.row, self.col + other.col)


MOVES_STR = '←↑→↓'
POSITIONS = Position(0, -1), Position(-1, 0), Position(0, 1), Position(1, 0)


class Move(Enum):
    LEFT = 0
    UP = auto()
    RIGHT = auto()
    DOWN = auto()

    def __repr__(self):
        return MOVES_STR[self.value]

    @property
    def position(self) -> Position:
        return POSITIONS[self.value]


# TODO: yes, structure could be massively improved, but I have no will to do it
# TODO: like... separate movables (rock) from static (key, code)
@dataclass
class Level:
    helltaker: Position
    moves: int
    grid: np.array
    spikes: np.array
    objectives: list[Position]  # TODO: necessary?
    has_key: bool = field(default=False)
    # no need for needs_key since lock blocks path
    has_code: bool = field(default=False)
    needs_code: bool = field(default=False)

    def __post_init__(self):
        assert self.grid.shape == self.spikes.shape
        # TODO: add objectives check

    def __eq__(self, other):
        return (self.grid == other.grid).all() and \
               self.has_key == other.has_key and \
               (self.spikes == other.spikes).all() and \
               self.moves == other.moves and \
               self.has_code == other.has_code and \
               self.needs_code == other.needs_code
        # TODO: what about self.moves?

        """
        return self.helltaker == other.helltaker and self.moves == other.moves and \
               np.all(self.grid == other.grid) and np.all(self.spikes == other.spikes) and \
               self.objectives == other.objectives and self.has_key == other.has_key
        """

    def __hash__(self):
        #print(self.grid.tostring())
        #print(hash(self.grid.tostring()))
        return hash((self.grid.tostring(), self.spikes.tostring(), self.moves, self.has_key, self.has_code, self.needs_code))

    def __str__(self):
        s = ''

        for i, row in enumerate(self.grid):
            for j, col in enumerate(row):
                if self.spikes[i][j] in (SPIKES_UP, SPIKES_ALWAYS):
                    #s += TermColors.BackgroundRed
                    s += TermColors.LightRed
                    s += TO_STR[col]
                    s += TermColors.ResetAll
                elif self.spikes[i][j] == SPIKES_DOWN:
                    #s += TermColors.BackgroundGreen
                    s += TermColors.LightGreen
                    s += TO_STR[col]
                    s += TermColors.ResetAll
                else:
                    s += TO_STR[col]
            s += '\n'
        s += f'{self.moves}\t{self.has_key}'

        return s

    def to_dot_label(self, initial_level: Level) -> str:
        # TODO: add spikes, etc.

        if self == initial_level:
            label = '<<TABLE BORDER="1" BGCOLOR="blue">'
        elif self.is_terminal():
            if self.is_goal():
                label = '<<TABLE BORDER="1" BGCOLOR="green">'
            else:
                # TODO: ok, this only makes sense with __eq__ using label, so...
                label = '<<TABLE BORDER="1" BGCOLOR="red">'
        else:
            label = '<<TABLE BORDER="1" BGCOLOR="white">'

        # TODO: since __eq__ doesn't include label...
        label += f'<TR><TD>moves: {self.moves}</TD></TR>'

        for i, row in enumerate(self.grid):
            label += '<TR>'
            for j, col in enumerate(row):
                if col == EMPTY:
                    label += '<TD BGCOLOR="white"> </TD>'
                elif col == WALL:
                    label += '<TD BGCOLOR="black"> </TD>'
                elif col == ROCK:
                    label += '<TD BGCOLOR="white">R</TD>'
                elif col == UNDEAD:
                    label += '<TD BGCOLOR="white">U</TD>'
                elif col == HELLTAKER:
                    label += '<TD BGCOLOR="white">H</TD>'
                elif col == GIRL:
                    label += '<TD BGCOLOR="white">G</TD>'
                elif col == KEY:
                    label += '<TD BGCOLOR="white">K</TD>'
                elif col == LOCK:
                    label += '<TD BGCOLOR="white">L</TD>'
                elif col == CODE_UNDER_ROCK:
                    label += '<TD BGCOLOR="white">C</TD>'
                elif col == CODE:
                    label += '<TD BGCOLOR="white">D</TD>'
                elif col == KEY_UNDER_ROCK:
                    label += '<TD BGCOLOR="white">Y</TD>'
                else:
                    raise NotImplementedError(i, j, col)
            label += '</TR>'

        label += '</TABLE>>'

        return label

    def __getitem__(self, item: Position) -> int:
        return self.grid[item.row][item.col]

    def __setitem__(self, key: Position, value: int) -> None:
        self.grid[key.row][key.col] = value

    @property
    def shape(self) -> tuple[int, int]:
        return self.grid.shape

    @staticmethod
    def load(fpath: str) -> Level:
        # TODO: need to implement code rock

        moves, grid, spikes, objectives = Level._load(fpath)

        grid = np.array(Level._parse_grid(grid))
        spikes = np.array(Level._parse_spikes(spikes))
        objectives = list(Level._parse_objectives(objectives))

        # find helltaker
        row, col = np.where(grid == HELLTAKER)
        assert len(row) == len(col) == 1
        helltaker = Position(row[0], col[0])

        return Level(helltaker=helltaker,
                     moves=moves,
                     grid=grid,
                     spikes=spikes,
                     objectives=objectives,
                     needs_code=CODE_UNDER_ROCK in grid)

    @staticmethod
    def _load(fpath: str) -> (int, list[str], list[str], list[str]):
        # TODO: use a grammar?

        moves = None
        grid = []
        spikes = []
        objectives = []

        stage = 0
        with open(fpath) as f:
            for line in f:
                line = line.strip()

                if stage == 0:
                    moves = int(line)
                    stage = 1
                elif stage == 1:
                    assert line == ''
                    stage = 2
                elif stage == 2:
                    assert 'grid' in line
                    stage = 3
                elif stage == 3:
                    if line == '':
                        stage = 4
                    else:
                        grid.append(line)
                elif stage == 4:
                    assert 'spikes' in line
                    stage = 5
                elif stage == 5:
                    if line == '':
                        stage = 6
                    else:
                        spikes.append(line)
                elif stage == 6:
                    assert 'objectives' in line
                    stage = 7
                elif stage == 7:
                    objectives.append(line)

        return moves, grid, spikes, objectives

    @staticmethod
    def _parse_grid(grid: list[str]) -> list[list[str]]:
        def parse(square):
            if square == '#':
                return WALL
            elif square == '.':
                return EMPTY
            elif square == 'H':
                return HELLTAKER
            elif square == 'U':
                return UNDEAD
            elif square == 'R':
                return ROCK
            elif square == 'G':
                return GIRL
            elif square == 'L':
                return LOCK
            elif square == 'K':
                return KEY
            elif square == 'C':
                return CODE_UNDER_ROCK
            else:
                raise NotImplementedError(square)

        return [[parse(square) for square in row] for row in grid]

    @staticmethod
    def _parse_spikes(spikes: list[str]) -> list[list[str]]:
        def parse(square):
            if square == '.':
                return EMPTY
            elif square == 'S':
                return SPIKES_UP
            elif square == 's':
                return SPIKES_DOWN
            elif square == 'T':
                return SPIKES_ALWAYS
            else:
                raise NotImplementedError(square)

        return [[parse(square) for square in row] for row in spikes]

    @staticmethod
    def _parse_objectives(objectives: list[str]):     # TODO: yield -> list[Position]:
        for i, row in enumerate(objectives):
            for j, col in enumerate(row):
                if col == '.':
                    pass
                elif col == 'O':
                    yield Position(i, j)
                else:
                    raise NotImplementedError(i, j, col)

    def clone(self) -> Level:
        return deepcopy(self)

    def do_move(self, move: Move) -> None:
        if self.is_terminal():
            raise IllegalMove('already endgame')

        self[self.helltaker] = E
        old_helltaker = self.helltaker
        self.helltaker += move.position

        # TODO: add key, lock
        if self[self.helltaker] == E:
            # empty new pos
            self[self.helltaker] = H
        elif self[self.helltaker] == U:
            self.helltaker = old_helltaker
            self[self.helltaker] = H

            if self[(new_pos := old_helltaker + move.position + move.position)] == E:
                self[old_helltaker + move.position] = E
                self[new_pos] = U
            else:
                self[old_helltaker + move.position] = E

            """
            # new pos with undead
            self[self.helltaker] = H

            if self[(new_pos := self.helltaker + move.position)] == E:
                # pushed
                self[new_pos] = U
            """
        elif self[self.helltaker] == R:
            # new pos with rock
            self.helltaker = old_helltaker
            self[self.helltaker] = H

            if self[(new_pos := self.helltaker + move.position + move.position)] == E:
                # pushed
                self[old_helltaker + move.position] = E
                self[new_pos] = R
            elif self[(new_pos := self.helltaker + move.position + move.position)] == K:
                # pushed
                self[old_helltaker + move.position] = E
                self[new_pos] = Y
            else:
                raise IllegalMove(f'{self.helltaker} - rock')
        elif self[self.helltaker] == W:
            raise IllegalMove(f'{self.helltaker} - wall')
        elif self[self.helltaker] == L:
            if self.has_key:
                self[self.helltaker] = H
            else:
                raise IllegalMove(f'{self.helltaker} - locked')
        elif self[self.helltaker] == K:
            self[self.helltaker] = H
            self.has_key = True
        elif self[self.helltaker] == C:
            self[self.helltaker] = D    # code

            self.helltaker = old_helltaker
            self[self.helltaker] = H

            if self[(new_pos := self.helltaker + move.position + move.position)] == E:
                # pushed
                self[new_pos] = C
            else:
                raise IllegalMove(f'{self.helltaker} - rock with code')
        elif self[self.helltaker] == D:
            self[self.helltaker] = H
            self.has_code = True
        elif self[self.helltaker] == Y:
            self.helltaker = old_helltaker
            self[self.helltaker] = H

            if self[(new_pos := self.helltaker + move.position + move.position)] == E:
                # pushed
                self[old_helltaker + move.position] = K
                self[new_pos] = R
            else:
                raise IllegalMove(f'{self.helltaker} - rock with key')
        elif self[self.helltaker] == G:
            raise IllegalMove(f'{self.helltaker} - girl')
        else:
            raise NotImplementedError(self[self.helltaker])

        # update spikes
        # this means spikes need to be compared too, I think
        for i, row in enumerate(self.spikes):
            for j, col in enumerate(row):
                if col == SPIKES_UP:
                    self.spikes[i][j] = SPIKES_DOWN
                elif col == SPIKES_DOWN:
                    self.spikes[i][j] = SPIKES_UP
                    if self.grid[i][j] == U:
                        self.grid[i][j] = E

        self.moves -= 1

        if self.spikes[self.helltaker.row][self.helltaker.col] in (SPIKES_UP, SPIKES_ALWAYS):
            self.moves -= 1

    def is_goal(self) -> bool:
        if self.needs_code:
            return self.has_code and self.helltaker in self.objectives
        else:
            return self.helltaker in self.objectives

    def is_terminal(self) -> int:
        return self.moves <= 0 or self.is_goal()

