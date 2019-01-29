class KeycloakClientError(Exception):
    def __init__(self, original_exc):
        """

        :param original_exc: Exception
        """
        self.original_exc = original_exc
        super(KeycloakClientError, self).__init__(*original_exc.args)

class KeycloakClientResponseError(KeycloakClientError):
    def __init__(self, response, **kwargs):
        self.response = response

        if hasattr(response, 'content') and response.content:
            try:
                import json

                data = response.content
                # on python 3 data is bytes .. we just asume encoding
                if isinstance(data, (bytes, bytearray)):
                    data = data.decode('utf-8', errors='ignore')

                content = json.loads(data)
                if 'errorMessage' in content:
                    self.message = content['errorMessage']

            except Exception as e:
                import logging
                logging.error('Unable to append response content to exception: %s' % (e, ))

        super(KeycloakClientResponseError, self).__init__(**kwargs)
