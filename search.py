# -*- coding: utf-8 -*-

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from puzzle import Level, Move, IllegalMove


@dataclass
class Node:
    level: Level
    move: Optional[Move] = field(default=None)
    parent: Optional[Node] = field(default=None)

    @property
    def solution(self) -> list[Move]:
        solution = []

        node = self
        while node is not None:
            if node.move is not None:
                solution.append(node.move)
            node = node.parent

        return list(reversed(solution))

    def successors(self):
        for move in Move:
            try:
                level = self.level.clone()
                level.do_move(move)
                yield Node(level=level, move=move, parent=self)
            except IllegalMove:
                pass


def search(level: Level, verbose=False):
    node = Node(level=level.clone())

    if node.level.is_goal():
        return node.solution

    frontier = [node]
    explored = set()

    while True:
        if not frontier:
            return None     # failure

        node = frontier.pop()
        if verbose:
            print(node.level)
        explored.add(node.level)

        for child in node.successors():
            if not(child.level in explored or child.level in [nd.level for nd in frontier]):
                if child.level.is_goal():
                    if verbose:
                        print(child.level)
                    return child.solution
                frontier.append(child)

    raise Exception     # should never get here


def search1(level: Level, verbose=False):
    levels = defaultdict(list)

    node = Node(level=level.clone())
    levels[node.level] = []

    if node.level.is_goal():
        return node.solution, levels

    frontier = [node]
    explored = set()

    while True:
        if not frontier:
            return None, levels     # failure

        node = frontier.pop()
        if verbose:
            print(node.level)
            print(node.level.is_goal(), node.level.is_terminal())
        explored.add(node.level)

        for child in node.successors():
            levels[node.level].append((child.move, child.level))
            if not(child.level in explored or child.level in [nd.level for nd in frontier]):
                if child.level.is_goal():
                    if verbose:
                        print(child.level)
                    return child.solution, levels
                frontier.append(child)

    raise Exception     # should never get here
