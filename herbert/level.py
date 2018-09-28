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

        points = _readint(file, 7, cls.NUMBER_PATTERN, 1, 1000000, nrows + 1, newline=True)
        max_bytes = _readint(file, 4, cls.NUMBER_PATTERN, 1, 1000, nrows + 2)

        return cls(field, points, max_bytes, nrows, ncols)

    def __init__(self, field, points, max_bytes, nrows, ncols):
        self.points = points
        self.max_bytes = max_bytes
        self.nrows = nrows
        self.ncols = ncols
        self._parse(field)

    def __call__(self):
        white_buttons = {}
        for r, c in self.white_buttons:
            white_buttons[(r, c)] = WhiteButton(r, c)

        gray_buttons = {}
        for r, c in self.gray_buttons:
            gray_buttons[(r, c)] = GrayButton(r, c, white_buttons.values())

        robot = Robot(*self.robot)

        return RuntimeEnvironment(self, robot, gray_buttons, white_buttons)

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


def _readint(file, size, pattern, lo, hi, row, newline=False):
    line = file.readline(size)
    error = ValueError('expected a positive integer in the range [%d, %d) at line %d: %s' % (lo, hi, row, line))

    if line.endswith('\n'):
        line = line[:-1]
    elif newline:
        raise error

    match = pattern.fullmatch(line)

    if match:
        result = int(line)

        if result < lo or result >= hi:
            raise error

        return result

    raise error


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


class Robot:
    MOVEMENT_DELTAS = (
        (-1, 0),    # up
        (0, 1),     # right
        (1, 0),     # down
        (0, -1)     # left
    )

    def __init__(self, row, col, direction):
        self.row = row
        self.col = col
        self.heading = ROBOT_DIRECTIONS.index(direction)
        self.trail = [(row, col)]

    def isup(self):
        return self.heading == 0

    def isright(self):
        return self.heading == 1

    def isdown(self):
        return self.heading == 2

    def isleft(self):
        return self.heading == 3

    def turn_left(self):
        self.heading = (self.heading - 1) % 4

    def turn_right(self):
        self.heading = (self.heading + 1) % 4

    def position_after_move(self):
        dr, dc = self.MOVEMENT_DELTAS[self.heading]

        return (self.row + dr, self.col + dc)

    def move_to(self, row, col):
        self.row = row
        self.col = col
        self.trail.append((row, col))


class GrayButton:
    def __init__(self, row, col, white_buttons):
        self.row = row
        self.col = col
        self.white_buttons = white_buttons

    def press(self):
        for white_button in self.white_buttons:
            white_button.unpress()


class WhiteButton:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.pressed = False

    def press(self):
        self.pressed = True

    def unpress(self):
        self.pressed = False


class RuntimeEnvironment:
    def __init__(self, level, robot, gray_buttons, white_buttons):
        self.level = level
        self.robot = robot
        self.gray_buttons = gray_buttons
        self.white_buttons = white_buttons
        self.total_buttons = len(white_buttons)
        self.npressed = 0       # the number of white buttons pressed
        self.max_npressed = 0   # the maximum number of white buttons pressed
        self.completed = False  # True iff all the white buttons have been pressed

    def step(self, command):
        if command == 's':
            row, col = pos = self.robot.position_after_move()

            if 0 <= row < self.level.nrows and 0 <= col < self.level.ncols and pos not in self.level.inaccessible_spots:
                self.robot.move_to(row, col)

                if pos in self.gray_buttons:
                    self.gray_buttons[pos].press()
                    self.npressed = 0
                elif pos in self.white_buttons:
                    self.white_buttons[pos].press()
                    self.npressed += 1
                    if self.npressed > self.max_npressed:
                        self.max_npressed = self.npressed

                    if not self.completed and self.white_buttons and self.npressed == self.total_buttons:
                        self.completed = True
        elif command == 'l':
            self.robot.turn_left()
        elif command == 'r':
            self.robot.turn_right()
        else:
            raise ValueError('not a command: %s' % command)

    def score(self, bytes):
        return calculate_score(self.level.points, self.level.max_bytes, self.total_buttons, self.npressed, bytes)

    def grid(self):
        new_grid = []

        for r, row in enumerate(self.level.grid):
            new_row = []
            for c, ch in enumerate(row):
                if ch in ROBOT_DIRECTIONS or ch == WHITE_BUTTON:
                    new_row.append(EMPTY)
                else:
                    new_row.append(ch)
            new_grid.append(new_row)

        for (r, c), white_button in self.white_buttons.items():
            new_grid[r][c] = 'b' if white_button.pressed else 'w'

        new_grid[self.robot.row][self.robot.col] = ROBOT_DIRECTIONS[self.robot.heading]

        return new_grid


def calculate_score(points, max_bytes, total_buttons, buttons, bytes):
    """Calculates the score for a level.

    points: the points assigned for solving the level (based on difficulty)
    max_bytes: the maximum number of bytes for the level
    total_buttons: the number of white buttons on the level
    buttons: the number of white buttons pressed
    bytes: the number of bytes actually used
    """

    if buttons == total_buttons and bytes <= max_bytes:
        # level solved
        return (points * max_bytes) // bytes

    # level unsolved
    assert buttons < total_buttons or bytes > max_bytes

    points_per_button = 0

    if bytes <= max_bytes:
        points_per_button = points // (2 * total_buttons)

    if max_bytes < bytes <= 2*max_bytes:
        points_per_button = points * (2*max_bytes - bytes) // (2 * max_bytes * total_buttons)

    return buttons * points_per_button
