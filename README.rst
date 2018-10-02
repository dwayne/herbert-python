Herbert
=======

Herbert is a game I first saw in the `Imagine Cup 2008 Algorithm Invitational <https://en.wikipedia.org/wiki/Imagine_Cup>`_.

The game requires you to solve a series of levels by writing small programs to
control a robot named Herbert. The simpler and more elegant your solution, the
more points you get.

It challenges your ability to see patterns and create algorithms to produce
those patterns.

Here's my clone of Herbert.

.. image:: https://raw.githubusercontent.com/dwayne/herbert-python/master/data/images/herbert.png

Enjoy!

Installation
------------

To install, simply use pip (or `pipenv`_):

.. code-block:: bash

    $ pip install herbert

Usage
-----

To run :code:`herbert` you need a **level** to solve and a **program**, that you
write, that attempts to solve the level.

Suppose the level is stored in :code:`level.txt` and that you wrote and saved
your solution in :code:`sol.h`. Then, you'd run :code:`herbert` as follows:

.. code-block:: bash

    $ herbert level.txt sol.h

It will open a `curses <https://en.wikipedia.org/wiki/Curses_%28programming_library%29>`_
based text user interface that allows you to run your program against the level
to determine if it solves the level and how many points your solution is worth.

**N.B.** The `data/example <https://github.com/dwayne/herbert-python/blob/master/data/example>`_
directory contains an example level along with 3 attempted solutions to the
level. You can use it to help you understand how the game works.

**An overview of the game**

A level consists of empty spaces (:code:`.`), walls (:code:`*`), white
(:code:`w`) and gray (:code:`g`) buttons, and a robot (:code:`u` means the robot
is facing upwards, :code:`r` means the robot is facing towards the right,
:code:`d` means the robot is facing downwards, or :code:`l` means the robot is
facing towards the left).

**N.B.** You can find an example level `here <https://github.com/dwayne/herbert-python/blob/master/data/example/level3.txt>`__.

On each level there are some white buttons. To solve a level you must press all
the white buttons. Your goal then is to program Herbert, in a language called
"h", to press all the white buttons while avoiding obstacles such as walls and
gray buttons (walls block Herbert's path and gray buttons reset any previously
pressed white buttons to their unpressed state).

You are only allotted a certain number of "bytes" (a unit of program size) per
level. Your program must use no more than this number of bytes.

Points are awarded for each white button pressed, a bonus is awarded for solving
the level, and extra points are awarded for solutions that use less than the
allotted maximum number of bytes.

**The "h" language**

It is a simple language that contains statements, procedures with zero or more
parameters and recursion. Check out the tutorial `here <https://github.com/dwayne/herbert-python/blob/master/data/resources/Tutorial.aspx.html>`__
to get a better understanding of the language.

You can find examples of the language in use `here <https://github.com/dwayne/herbert-python/blob/master/data/example/sol3a.h>`__,
`here <https://github.com/dwayne/herbert-python/blob/master/data/example/sol3b.h>`__
and `here <https://github.com/dwayne/herbert-python/blob/master/data/example/sol3c.h>`__.

**Challenge**

Try to solve the following levels (see `data/levels <https://github.com/dwayne/herbert-python/blob/master/data/levels>`_):

- `Level 1 <https://github.com/dwayne/herbert-python/blob/master/data/levels/level1.txt>`_
- `Level 2 <https://github.com/dwayne/herbert-python/blob/master/data/levels/level2.txt>`_
- `Level 3 <https://github.com/dwayne/herbert-python/blob/master/data/levels/level3.txt>`_
- `Level 4 <https://github.com/dwayne/herbert-python/blob/master/data/levels/level4.txt>`_
- `Level 5 <https://github.com/dwayne/herbert-python/blob/master/data/levels/level5.txt>`_

Development
-----------

Recommended tools:

 - `pyenv <https://github.com/pyenv/pyenv>`_
 - `pipenv`_

Clone the repository and install the dependencies:

.. code-block:: bash

    $ git clone git@github.com:dwayne/herbert-python.git
    $ cd herbert-python
    $ pipenv shell
    $ pipenv install --dev

You're now all set to begin development.

Testing
-------

Tests are written using the built-in unit testing framework, `unittest <https://docs.python.org/3/library/unittest.html>`_.

Run all tests.

.. code-block:: bash

    $ python -m unittest

Run a specific test module.

.. code-block:: bash

    $ python -m unittest tests.test_interpreter

Run a specific test case.

.. code-block:: bash

    $ python -m unittest tests.test_interpreter.ExamplesTestCase.test_example10

Resources
---------

- `Herbert Programming Challenge <https://herbert.wildnoodle.com/>`_ by `Wild Noodle <http://www.wildnoodle.com/>`_
- `Herbert Online Judge <http://herbert.tealang.info/>`_
- `uHerbert <http://membres-lig.imag.fr/benyelloul/uherbert/index.html>`_

.. _pipenv: https://github.com/pypa/pipenv
