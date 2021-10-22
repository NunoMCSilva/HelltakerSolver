# -*- coding: utf-8 -*-

from __future__ import annotations

from puzzle import Level, Move
from search import search, search1, Node


def apply_moves(level, solution):
    print(level)
    print()
    if solution:
        for move in solution:
            level.do_move(move)
            print(level)
            print()
    print(solution)


def do_dot(fpath, level, levels, write=True):
    print(len(levels))

    # get all levels
    st = set()
    for k, v in levels.items():
        st.add(k)
        for _, v1 in v:
            st.add(v1)

    print(len(st))

    if write:
        level_str = fpath.split("/")[-1].split(".")[0]
        with open(f'{level_str}.dot', 'w') as f:
            f.write(f'digraph {level_str} ')
            f.write('{')
            f.write('\n')

            #f.write(f'\troot="{hash(level)}";')

            for lv in st:
                f.write('\t')
                f.write(f'"{hash(lv)}"')
                f.write(' ')
                f.write(f'[label={lv.to_dot_label(level)}];')
                f.write('\n')

            f.write('\n')

            for k, v in levels.items():
                for m1, v1 in set(v):
                    f.write('\t')
                    f.write(f'"{hash(k)}" -> "{hash(v1)}" [label="{m1!r}"];')
                    f.write('\n')

            f.write('}')
            f.write('\n')


def compress_solution(solution):
    # TODO: there is probably a functools of itertools for this

    if solution is None:
        return

    current_move = None
    current_num = 0

    for move in solution:
        if current_move == move:
            current_num += 1
        else:
            if current_move is not None:
                # print(current_num, current_move)
                yield current_num, current_move
            current_move = move
            current_num = 1
    # print(current_num, current_move)
    yield current_num, current_move


def level(fpath, search_verbose=False):
    print(fpath)
    level_ = Level.load(fpath)
    print(level_)
    print()

    # solution = search(level, verbose=True)
    solution, levels = search1(level_, verbose=search_verbose)
    print(solution)
    print()

    apply_moves(level_, solution)

    do_dot(fpath, Level.load(fpath), levels, write=False)
    print(sol := ' '.join(f'{n}{m!r}' for n, m in compress_solution(solution)))

    return sol


def main():
    # 1st level - solution works in actual game
    assert level('levels/level1.txt', search_verbose=False) == '1↓ 1← 2↓ 5← 1↓ 1← 2↓ 2→ 2↑ 4→ 1↓ 1→'

    # adds static spikes - solution works in actual game
    assert level('levels/level2.txt', search_verbose=False) == '1→ 6↑ 3→ 1↓ 2→ 4↓ 2← 1↓'

    # adds key and lock - solution works in actual game
    assert level('levels/level3.txt', search_verbose=False) == '5← 4↓ 2← 1↑ 1↓ 8→ 6↑'

    # adds code under rock - solution works in actual game
    assert level('levels/level4.txt', search_verbose=False) == '3↓ 1→ 2↓ 1→ 2↑ 1→ 2↓ 1→ 2↑ 2→ 2↓ 2→ 2↑'

    # adds dynamic spikes - solution works in actual game
    assert level('levels/level5.txt', search_verbose=False) == '4↓ 2→ 1↑ 3→ 1↓ 1↑ 1← 2↑ 2← 3↑ 2→'

    # no gameplay change: angel girl - solution works in actual game
    assert level('levels/level6.txt', search_verbose=False) ==\
           '1← 1↓ 2→ 2↓ 2← 1↓ 2← 2↓ 4→ 2↑ 2← 4↓ 3→ 2↑ 4→ 2↓ 2← 1↓ 2→'

    # no gameplay change: just showing "interlocked" dynamic spikes - solution works in actual game
    assert level('levels/level7.txt', search_verbose=False) == '2↑ 1↓ 2← 2↑ 1→ 3↓ 3← 4↑ 3→ 1↑ 1↓ 3→ 2↑ 2→ 2↑'

    # objective is not getting within 1 square of demon girl, but in front of table she's sitting at -
    # solution works in actual game
    assert level('levels/level8.txt', search_verbose=False) == '1→ 9↑ 2←'
    # TODO: check graph. doesn't expand UP,UP... mistake in graph or... didn't expand because?

    # no gameplay change (no demon girl, just a door) -- TODO: test sol
    assert level('levels/level9.txt', search_verbose=False) == '1→ 2↑ 4→ 1↓ 2→ 1← 3↑ 4→ 2↓ 2→ 2↑ 1→ 3← 3↑ 1← 1↑'


def main1():
    level = Level.load('levels/level8.txt')
    print(level)

    level.do_move(Move.UP)
    print(level)

    level.do_move(Move.UP)
    print(level)

    level.do_move(Move.UP)
    print(level)

    level.do_move(Move.UP)
    print(level)

    level.do_move(Move.UP)
    print(level)

    level.do_move(Move.UP)
    print(level)
    level.do_move(Move.UP)
    print(level)

    level.do_move(Move.UP)
    print(level)
    level.do_move(Move.UP)
    print(level)

    level.do_move(Move.UP)
    print(level)
    level.do_move(Move.UP)
    print(level)

    level.do_move(Move.UP)
    print(level)


def main2():
    level = Level.load('levels/level5.txt')
    print(level)

    level.do_move(Move.DOWN)
    print(level)

    level.do_move(Move.DOWN)
    print(level)

    level.do_move(Move.DOWN)
    print(level)

    level.do_move(Move.DOWN)
    print(level)


def main3():
    level = Level.load('levels/level6.txt')
    print(level)

    for move in [Move.LEFT, Move.DOWN, Move.RIGHT, Move.RIGHT, Move.DOWN]:
        print(move)
        level.do_move(move)
        print(level)


if __name__ == '__main__':
    main()
