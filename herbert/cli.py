import argparse
import logging

from . import constants, ui
from .error import HerbertError


DEFAULT_FPS = 4


def main(args=None):
    ns = _argument_parser().parse_args(args)

    try:
        ui.main(ns.level, ns.program, DEFAULT_FPS)
    except HerbertError:
        logging.exception('Sorry, exiting the program due to an error.')
        return 1
    except:
        logging.exception('Sorry, an unexpected error occurred.')
        return 1

    return 0


def _argument_parser():
    parser = argparse.ArgumentParser(
        prog=constants.PROGRAM_NAME.lower(),
        description='%s is a game that requires you to write small programs to control a robot to solve various levels.' % constants.PROGRAM_NAME
    )

    parser.add_argument('level',
        type=argparse.FileType('r', encoding='utf-8'),
        help='a level to solve'
    )

    parser.add_argument('program',
        type=argparse.FileType('r', encoding='utf-8'),
        help='a program to run against the level')

    return parser
