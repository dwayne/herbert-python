import curses
import os
import time

from . import constants, counter, interpreter, parser
from .error import LevelError, ProgramError, SyntaxError
from .level import Level
from .util import cachedmethod


def main(level_file, program_file, fps):
    curses.wrapper(UI(load(level_file, program_file, fps)))


def load(level_file, program_file, fps):
    level = load_level(level_file)
    program = load_program(program_file)

    return Context(level, program, fps)


def load_level(file):
    try:
        level = Level.fromfile(file)
    except ValueError as e:
        raise LevelError('Sorry, we were unable to parse the level: %s.' % e) from e
    except OSError as e:
        raise LevelError('Sorry, we were unable to operate on the level file.') from e
    except:
        raise LevelError('Sorry, an unexpected error occurred while accessing the level file.')
    else:
        level.name = os.path.splitext(os.path.basename(file.name))[0]
        return level


def load_program(file):
    try:
        source_code = file.read()
    except OSError as e:
        raise ProgramError('Sorry, we were unable to operate on the program file.') from e
    except:
        raise ProgramError('Sorry, an unexpected error occurred while accessing the program file.')
    else:
        try:
            return Program(source_code)
        except SyntaxError as e:
            raise ProgramError('Sorry, we were unable to parse the program due to a syntax error.') from e


class Program:
    def __init__(self, source_code):
        self.ast = parser.parse(source_code)
        self.source_code = source_code

    @cachedmethod
    def bytes(self):
        return counter.count_bytes(self.ast)

    @cachedmethod
    def lines(self):
        return self.source_code.split('\n')

    def commands(self):
        return interpreter.interp(self.ast)


class Context:
    def __init__(self, level, program, fps):
        self.level = level
        self.program = program
        self.draw_callback = None
        self.fps = fps
        self._spf = 1 / fps

    @property
    def total_points(self):
        return self._re.level.points

    @property
    def bytes(self):
        return self.program.bytes()

    @property
    def source_code_lines(self):
        return self.program.lines()

    @property
    def max_bytes(self):
        return self.level.max_bytes

    @property
    def level_name(self):
        return self.level.name

    @property
    def completed(self):
        return self._re.completed

    @property
    def grid(self):
        return self._re.grid()

    def reset(self, draw_callback=None):
        self.running = False
        self.max_points = self.current_points = 0
        self._re = self.level()
        self._commands = self.program.commands()
        self._start_time = None
        self._run_now = False

        if draw_callback is None:
            self._draw()
        else:
            draw_callback()

    def start(self):
        if not self.running and self._commands:
            self.running = True
            self._start_time = time.perf_counter()
            self._run_now = True
            self._draw()

    def stop(self):
        if self.running:
            self.running = False
            self._start_time = None
            self._run_now = False
            self._draw()

    def step(self):
        if not self.running:
            if self._move():
                self._draw()

    def update(self):
        if self.running:
            end_time = time.perf_counter()
            elapsed_time = end_time - self._start_time

            if self._run_now or elapsed_time > self._spf:
                self._run_now = False
                if self._move():
                    self._draw()

            if elapsed_time > self._spf:
                self._start_time = end_time

    def _move(self):
        if self._commands:
            try:
                command = next(self._commands)
            except StopIteration:
                self._commands = None
                self.running = False
            else:
                self._re.step(command)
                self.current_points = self._re.score(self.bytes)
                self.max_points = max(self.max_points, self.current_points)

            return True

        return False

    def _draw(self):
        if self.draw_callback is not None:
            self.draw_callback()


class UI:
    def __init__(self, context):
        self.context = context
        self.context.draw_callback = self.redraw

    def __call__(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)

        self.stdscr = stdscr
        self.windows = windows = []

        ctx = self.context

        # The contents of these windows never change
        windows.append(Title())
        windows.append(SourceCode(ctx))

        # The contents of these windows can change
        windows.append(Status(ctx))
        windows.append(Runtime(ctx))
        windows.append(Footer(ctx))

        ctx.reset(self.draw)

        while True:
            c = stdscr.getch()

            if c == ord('g'):
                ctx.start()
            elif c == ord('s'):
                ctx.stop()
            elif c == ord('n'):
                ctx.step()
            elif c == ord('r'):
                ctx.reset()
            elif c == ord('q'):
                break

            ctx.update()

    def draw(self):
        self.stdscr.noutrefresh()
        for window in self.windows:
            window.draw()
        curses.doupdate()

    def redraw(self):
        self.stdscr.noutrefresh()
        for window in self.windows[2:]:
            window.draw()
        curses.doupdate()


class AddString:
    def __init__(self, x, y, s):
        self.x = x
        self.y = y
        self.s = s

    def __call__(self, window):
        window.addstr(self.y, self.x, self.s)


class Window:
    def __init__(self, x, y, width, height):
        self._handle = curses.newwin(height, width, y, x)
        self._actions = []

    def add_string(self, x, y, s):
        self._actions.append(AddString(x, y, s))

    def draw(self):
        self._handle.clear()

        for action in self._actions:
            action(self._handle)
        self._actions = []

        self._handle.noutrefresh()


class WindowWithBorders(Window):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

        self._parent = self._handle
        self._handle = curses.newwin(height-2, width-2, y+1, x+1)

    def draw(self):
        self._parent.box()
        self._parent.noutrefresh()
        super().draw()


class Title(Window):
    def __init__(self):
        super().__init__(0, 0, curses.COLS, 1)

    def draw(self):
        self.add_string(1, 0, '%s %s' % (constants.PROGRAM_NAME, constants.VERSION))
        super().draw()


class Status(Window):
    def __init__(self, context):
        super().__init__(0, 1, curses.COLS, 1)
        self.context = context

    def draw(self):
        max_points = self.context.max_points
        total_points = self.context.total_points
        current_points = self.context.current_points
        bytes = self.context.bytes
        max_bytes = self.context.max_bytes
        level_name = self.context.level_name
        solved_status = '(' + ('Solved' if self.context.completed else 'Unsolved') + ')'

        self.add_string(1, 0, 'Points %d/%d    (%d now)    Bytes: %d    (Max %d)    %s    %s' % (max_points, total_points, current_points, bytes, max_bytes, level_name, solved_status))
        super().draw()


_WIDTH = 1+1+25+24+1+1
_HEIGHT = 1+25+1


class Runtime(WindowWithBorders):
    def __init__(self, context):
        super().__init__(0, 2, _WIDTH, _HEIGHT)
        self.context = context

    def draw(self):
        for r, row in enumerate(self.context.grid):
            self.add_string(1, r, ' '.join(row))
        super().draw()


class SourceCode(WindowWithBorders):
    def __init__(self, context):
        super().__init__(_WIDTH, 2, _WIDTH, _HEIGHT)
        self.context = context

    def draw(self):
        for row, line in enumerate(self.context.source_code_lines):
            self.add_string(1, row, line)
        super().draw()


class Footer(WindowWithBorders):
    def __init__(self, context):
        super().__init__(0, 2+_HEIGHT, 2*_WIDTH, 3)
        self.context = context

    def draw(self):
        go_stop_msg = '(s) STOP' if self.context.running else '(g) GO'

        self.add_string(1, 0, '%s, (n) STEP, (r) RESET, (q) QUIT' % go_stop_msg)
        super().draw()
