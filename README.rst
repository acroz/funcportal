funcportal
==========

*funcportal* runs your Python functions as a web API, with no code changes
required.

Usage
-----

Given a Python module like ``code.py`` below:

.. code-block:: python

    # code.py
    def address(name):
        """Get someone's address."""
        if name == 'Jane':
            return '1 Main Street'
        elif name == 'John':
            return '2 Alternative Avenue'
        else:
            return None

You can serve the function ``address()`` as a web API with *funcportal* on the
command line:

.. code-block:: bash

    $ funcportal code:address

and you can then make HTTP POST requests to it, for example with the Python
*requests* library:

.. code-block:: python

    import requests
    response = requests.post(
        'http://localhost:5000/address',
        json={'name': 'Jane'}
    )
    address = response.json()['result']
