# HelltakerSolver
Helltaker Solver

Developed this over two days. Produces solutions for levels 1-9.
Needs a LOT of refactoring and improvement but works.

# Node Expansion Graphs
Change main.py from

`do_dot(fpath, Level.load(fpath), levels, write=False)`

to

`do_dot(fpath, Level.load(fpath), levels, write=True)`

to write graphviz files showing all expanded nodes.

I use show.sh on Linux to see most of them, since converting to images has issues.
Raster images get too pixelated to see.
SVG gets too big to open (even Inkscape can't handle the largest).
