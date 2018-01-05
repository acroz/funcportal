from setuptools import setup


setup(
    name='portal',
    description='Serve functions as an API',
    packages=['portal'],
    install_requires=[
        'flask',
        'requests',
        'six'
    ],
    entry_points={
        'console_scripts': [
            'portal=portal.main:main'
        ]
    }
)
