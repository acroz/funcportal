import os
import subprocess
import time

import requests
import pytest


TEST_MODULE = """
def multiply(x, y):
    return x * y

def exponent(base, power=2):
    return base ** power
"""

TEST_CONFIG = """
routes:
  - module: module
    function: multiply
    endpoint: /fromconfig/multiply
  - module: module
    function: multiply
    endpoint: /async/multiply
    async: true
"""


@pytest.fixture(scope='session')
def srcdir(tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp('tmp')
    tmpdir.join('module.py').write(TEST_MODULE)
    return tmpdir


@pytest.fixture(scope='session')
def server(srcdir):
    config = srcdir.join('portal.yaml')
    config.write(TEST_CONFIG)
    env = os.environ.copy()
    env['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + ':' + str(srcdir)
    process = subprocess.Popen(
        ['funcportal', 'server', 'module:multiply', 'module:exponent',
         '--config', str(config)],
        env=env
    )
    time.sleep(1)  # TODO: Check for readiness
    assert process.poll() is None, 'The funcportal process failed'
    yield 'http://127.0.0.1:5000'
    process.terminate()
    process.wait()


@pytest.fixture(scope='session')
def worker(srcdir):
    env = os.environ.copy()
    env['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + ':' + str(srcdir)
    process = subprocess.Popen(['funcportal', 'worker'], env=env)
    yield
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


def test_asynchronous(server, worker):
    url = server + '/async/multiply'
    response = requests.post(url, json={'x': 2, 'y': 3})
    assert response.status_code == 202
    result_token = response.json()['result_token']

    for _ in range(10):
        time.sleep(0.1)
        response = requests.get(url + '/{}'.format(result_token))
        print(response.text)
        if response.status_code != 404:
            break
    else:
        pytest.fail('result did not become available')

    assert response.status_code == 200
    assert response.json() == {'result': 6}
