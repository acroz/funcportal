from setuptools import setup


setup(
    name='ingang',
    description="Ingang t' yer functions",
    packages=['ingang'],
    install_requires=[
        'flask',
        'requests',
        'six'
    ],
    entry_points={
        'console_scripts': [
            'ingang=ingang.main:main'
        ]
    }
)
