import requests

from funcportal import errorcode


class ClientError(Exception):
    pass


class FuncPortalClient(object):

    def __init__(self, url):
        self.url = url
        self.session = requests.Session()

    def _call(self, endpoint, **kwargs):

        response = self.session.post(endpoint, json=kwargs)

        if response.status_code == 200:
            return response.json()['result']

        elif response.status_code == 400:
            code = response.json()['error_code']
            if code == errorcode.MISSING_ARGUMENTS:
                pass
            elif code == errorcode.MALFORMATTED_JSON:
                raise ClientError('bad content sent to server')
            else:
                raise ClientError('unrecognised error code "{}"'.format(code))

        elif response.status_code == 500:
            raise ClientError(
                'an error occurred on the server when handling the response'
            )

        else:
            raise ClientError(
                'unexpected response from server with status {}'
                .format(response.status_code)
            )
