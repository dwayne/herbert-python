from setuptools import setup


setup(
    install_requires=['lark-parser==0.6.4'],
    entry_points={
        'console_scripts': [
            'herbert=herbert.cli:main'
        ]
    }
)
