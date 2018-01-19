import os
import subprocess
import requests
import pytest


TEST_MODULE = """
def multiply(x, y):
    return {"result": x * y}

def exponent(base, power=2):
    return {"result": base ** power}
"""


@pytest.fixture
def server(tmpdir):
    tmpdir.join('module.py').write(TEST_MODULE)
    env = os.environ.copy()
    env['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + ':' + str(tmpdir)
    process = subprocess.Popen(
        ['portal', 'module:multiply', 'module:exponent'],
        env=env
    )
    yield 'http://localhost:5000'
    process.terminate()
    process.wait()


def test_portal(server):
    url = server + '/multiply'
    response = requests.post(url, json={'x': 2, 'y': 3})
    assert response.json() == {'result': 6}


def test_optional_arguments(server):
    url = server + '/exponent'
    response = requests.post(url, json={'base': 3, 'power': 4})
    assert response.json() == {'result': 81}


def test_optional_argument_omitted(server):
    url = server + '/exponent'
    response = requests.post(url, json={'base': 3})
    assert response.json() == {'result': 9}


def test_missing_argument(server):
    url = server + '/multiply'
    response = requests.post(url, json={'x': 2})
    body = response.json()
    assert body['error'] is True
    assert "missing 1 required positional argument: 'y'" in body['description']
    assert body['arguments'] == {
        'required': [{'name': 'x'}, {'name': 'y'}],
        'optional': []
    }
