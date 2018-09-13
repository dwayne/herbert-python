import re

from .util import pluralize


EMPTY = '.'
WALL = '*'
GRAY_BUTTON = 'g'
WHITE_BUTTON = 'w'
ROBOT_DIRECTIONS = ('u', 'r', 'd', 'l')
ALL_SYMBOLS = (EMPTY, WALL, GRAY_BUTTON, WHITE_BUTTON) + ROBOT_DIRECTIONS


class Level:
    LINE_PATTERN = re.compile(r'[.*gwurdl]+\n')
    NUMBER_PATTERN = re.compile(r'\d+')

    @classmethod
    def fromfile(cls, file, *, nrows=25, ncols=25):
        if nrows < 1:
            raise ValueError('the number of rows must be greater than or equal to 1: %s' % nrows)

        if ncols < 1:
            raise ValueError('the number of columns must be greater than or equal to 1: %s' % ncols)

        field = ''

        for i in range(nrows):
            line = file.readline(ncols + 1)
            match = cls.LINE_PATTERN.fullmatch(line)

            if match and match.end() == ncols + 1:
                field += line
            else:
                if match is None:
                    if line == '':
                        raise ValueError('expected %d %s but got %d' % (nrows, pluralize(nrows, 'line', 'lines'), i))
                    elif line == '\n':
                        raise ValueError('line %d is an empty line' % (i + 1))
                    else:
                        if re.fullmatch('[.*gwurdl]+', line):
                            raise ValueError('line %d is not %d %s long' % (i + 1, ncols, pluralize(ncols, 'character', 'characters')))
                        else:
                            raise ValueError('illegal character found at line %d' % (i + 1))
                else:
                    raise ValueError('line %d is not %d %s long' % (i + 1, ncols, pluralize(ncols, 'character', 'characters')))

        field = field[:-1]

        line = file.readline(5)
        if line.endswith('\n'):
            line = line[:-1]

        match = cls.NUMBER_PATTERN.fullmatch(line)
        error = ValueError('expected a positive integer in the range [1, 1000) at line %d: %s' % (nrows + 1, line))

        if match:
            max_bytes = int(line)
            if max_bytes < 1 or max_bytes >= 1000:
                raise error
        else:
            raise error

        return cls(field, max_bytes, nrows, ncols)

    def __init__(self, field, max_bytes, nrows, ncols):
        self.max_bytes = max_bytes
        self.nrows = nrows
        self.ncols = ncols
        self._parse(field)

    def _parse(self, field):
        # Step 1: Convert the field to a grid
        grid = []

        lines = field.splitlines()
        assert len(lines) == self.nrows

        for line in lines:
            assert len(line) == self.ncols
            grid.append(list(line))

        # Step 2: Get the robot, buttons and walls
        robot = None
        gray_buttons = []
        white_buttons = []
        walls = []
        inaccessible_spots = set()
        hseen = set()
        vseen = set()

        for r in range(self.nrows):
            for c in range(self.ncols):
                ch = grid[r][c]

                if ch in ROBOT_DIRECTIONS:
                    if robot is None:
                        robot = (r, c, ch)
                    else:
                        raise ValueError('too many robots, found another one at (%d, %d)' % (r + 1, c + 1))
                elif ch == GRAY_BUTTON:
                    gray_buttons.append((r, c))
                elif ch == WHITE_BUTTON:
                    white_buttons.append((r, c))
                elif ch == WALL:
                    proper_wall = False

                    if (r, c) in hseen:
                        proper_wall = True
                    else:
                        extent = _extend_horizontally(grid, hseen, r, c, self.nrows, self.ncols)
                        if extent > 0:
                            proper_wall = True
                            wall = HWall(r, c, extent)
                            walls.append(wall)
                            inaccessible_spots.update(wall)

                    if (r, c) in vseen:
                        proper_wall = True
                    else:
                        extent = _extend_vertically(grid, vseen, r, c, self.nrows, self.ncols)
                        if extent > 0:
                            proper_wall = True
                            wall = VWall(r, c, extent)
                            walls.append(wall)
                            inaccessible_spots.update(wall)

                    if not proper_wall:
                        raise ValueError('improper wall at (%d, %d)' % (r + 1, c + 1))
                else:
                    assert ch == EMPTY

        if robot is None:
            raise ValueError('no robot found')

        self.grid = grid
        self.robot = robot
        self.gray_buttons = gray_buttons
        self.white_buttons = white_buttons
        self.walls = walls
        self.inaccessible_spots = inaccessible_spots


def _extend_horizontally(grid, hseen, row, col, nrows, ncols):
    len = 0
    hseen.add((row, col))

    while col+1 < ncols and grid[row][col+1] == WALL:
      col += 1
      len += 1
      hseen.add((row, col))

    return len


def _extend_vertically(grid, vseen, row, col, nrows, ncols):
    len = 0
    vseen.add((row, col))

    while row+1 < nrows and grid[row+1][col] == WALL:
      row += 1
      len += 1
      vseen.add((row, col))

    return len


class Wall:
    def __init__(self, row, col, extent):
        self.row = row
        self.col = col
        self.extent = extent


class HWall(Wall):
    def __iter__(self):
        for i in range(self.extent + 1):
            yield (self.row, self.col + i)


class VWall(Wall):
    def __iter__(self):
        for i in range(self.extent + 1):
            yield (self.row + i, self.col)
