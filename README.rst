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

    $ funcportal server code:hello

and you can then make HTTP POST requests to it, for example with the Python
*requests* library:

.. code-block:: python

    >>> import requests
    >>> response = requests.post(
    >>>     'http://localhost:5000/hello',
    >>>     json={'name': 'Jane'}
    >>> )
    >>> print(response.status_code)
    200
    >>> print(response.json())
    {'result': 'Hello, Jane!'}

Alternatively, use a configuration file to specify the functions to serve and
their endpoints. The configuration file is YAML formatted:

.. code-block:: yaml

    routes:
      - module: code
        function: hello
        endpoint: /hello
      - module: code
        function: other
        endpoint: /other

As with the command line interface, the module and function indicate the code
to be run, and the endpoint is the address on the server that the API will be
run.

Load endpoints from the configuration file with the ``-c``/``--config`` command
line option:

.. code-block:: bash

    $ funcportal server -c config.yaml

Asynchronous execution
----------------------

When executing longer running function calls, you won't want to hold open the
HTTP connection for a long time, as it increases the risk of failure (as well
as making management of server resources more difficult). To avoid this, use
*funcportal*'s asynchronous execution feature. To enable asynchronous
execution, set the ``async`` flag to true for a route in the configuration
file:

.. code-block:: yaml

    routes:
      - module: code
        function: slow
        endpoint: /slow
        async: true

**Important:** To execute functions asynchonously, you need to have redis
server installed and running, and then also run one or more *funcportal* worker
processes separately from the server process(es):

.. code-block:: bash

    $ funcportal worker

Then, when you call this endpoint, instead of waiting until the function has
finished running and returning the result (if any), a response will be returned
immediately with a token that can be redeemed later for the result:

.. code-block:: python

    >>> response = requests.post(
    >>>     'http://localhost:5000/slow',
    >>>     json={'input': 4}
    >>> )
    >>> print(response.status_code)
    202
    >>> print(response.json())
    {'result_token': '3bf409d0-4b91-4e75-87e4-c377f2f9dbf6'}

You can then poll the original endpoint plus the result token with an HTTP GET
to retrieve the result when ready. Before the result is ready, a 404 NOT FOUND
status is returned:

.. code-block:: python

    >>> response = requests.get(
    >>>     'http://localhost:5000/slow/3bf409d0-4b91-4e75-87e4-c377f2f9dbf6'
    >>> )
    >>> print(response.status_code)
    404
    >>> print(response.json())
    {'error': 'Job result not available.'}

Once the job is finished, a 200 OK status is returned along with the result:

.. code-block:: python

    >>> response = requests.get(
    >>>     'http://localhost:5000/slow/3bf409d0-4b91-4e75-87e4-c377f2f9dbf6'
    >>> )
    >>> print(response.status_code)
    200
    >>> print(response.json())
    {'result': 79}
