import os
import subprocess
import time

import requests
import pytest


TEST_MODULE = """
def multiply(x, y):
    return {"result": x * y}

def exponent(base, power=2):
    return {"result": base ** power}
"""

TEST_CONFIG = """
routes:
  - module: module
    function: multiply
    endpoint: /fromconfig/multiply
"""


@pytest.fixture(scope='session')
def server(tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp('tmp')
    tmpdir.join('module.py').write(TEST_MODULE)
    config = tmpdir.join('portal.yaml')
    config.write(TEST_CONFIG)
    env = os.environ.copy()
    env['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + ':' + str(tmpdir)
    process = subprocess.Popen(
        ['funcportal', 'module:multiply', 'module:exponent',
         '--config', str(config)],
        env=env
    )
    time.sleep(1)  # TODO: Check for readiness
    assert process.poll() is None, 'The funcportal process failed'
    yield 'http://127.0.0.1:5000'
    process.terminate()
    process.wait()


def test_funcportal(server):
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
    assert response.status_code == 400
    body = response.json()
    assert "missing 1 required positional argument: 'y'" in body['error']
    assert body['arguments'] == {
        'required': [{'name': 'x'}, {'name': 'y'}],
        'optional': []
    }
