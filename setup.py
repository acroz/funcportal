from setuptools import setup


setup(
    name='funcportal',
    version='0.0.0',
    description='Serve Python functions as web APIs',
    packages=['funcportal'],
    install_requires=[
        'flask',
        'requests',
        'six'
    ],
    entry_points={
        'console_scripts': [
            'funcportal=funcportal.main:main'
        ]
    }
)
