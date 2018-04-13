from setuptools import setup

from funcportal.version import __version__


setup(
    name='funcportal',
    version=__version__,
    description='Serve Python functions as web APIs',
    packages=['funcportal'],
    install_requires=[
        'flask',
        'requests',
        'six',
        'pyyaml'
    ],
    entry_points={
        'console_scripts': [
            'funcportal=funcportal.main:main'
        ]
    }
)
