from setuptools import setup, find_packages

NAME = "awfulhospital_checker"
DESCRIPTION = "A discord bot that lets people know when awful hospital has updated"
AUTHOR = "Marlyn"
REQUIRES_PYTHON = '>=3.7.0'
VERSION = None

print("discord.py doesn't work on 3.7+ unless you use the dev version, but it's not published there. However, pip doesn't support installing from external repositories inline. You will need to install the updated version of discord.py by hand until one party reconciles this.")
print("pip install https://github.com/Rapptz/discord.py/archive/rewrite.zip#egg=discord.py[voice]")

REQUIRED = [
        "xdg",
        "bs4",
        "aiohttp",
        "async_timeout",
        "asynccmd",
        ]
#REQUIRED = [
        # Using this branch bc older ones don't work with 3.7
#        "discord.py@https://github.com/Rapptz/discord.py/archive/async.zip#egg=discord.py[voice]",
#        ]

setup(
        name = NAME,
        version = VERSION,
        author = AUTHOR,
        description = DESCRIPTION,
        packages = find_packages(exclude=['docs', 'tests']),
        install_requires = REQUIRED,
        license='MIT',
        entry_points = {
            'console_scripts': ['ah_checker = ah_checker.__main__:main'],
            },
)
