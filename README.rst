funcportal
==========

.. image:: https://travis-ci.org/acroz/funcportal.svg?branch=master
    :target: https://travis-ci.org/acroz/funcportal

.. image:: https://badge.fury.io/py/funcportal.svg
    :target: https://pypi.org/project/funcportal/

*funcportal* runs your Python functions as a web API, with no code changes
required.

Usage
-----

Given a Python module like ``code.py`` below:

.. code-block:: python

    # code.py
    def hello(name):
        return f'Hello, {name}!'

You can serve the function ``hello()`` as a web API with *funcportal* on the
command line:

.. code-block:: bash

    $ funcportal code:hello

and you can then make HTTP POST requests to it, for example with the Python
*requests* library:

.. code-block:: python

    >>> import requests
    >>> response = requests.post(
    >>>     'http://localhost:5000/hello',
    >>>     json={'name': 'Jane'}
    >>> )
    >>> result = response.json()['result']
    >>> print(result)
    Hello, Jane!
