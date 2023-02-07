#!/usr/bin/env python3.10

""" Sign all HTTP requests by `httpx` to AWS when gated via IAM, as required according to AWS Docs. """

import logging
import os
from collections.abc import Generator
from typing import Optional

import boto3
import httpx
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import (
    Credentials,
    ReadOnlyCredentials,
    RefreshableCredentials,
)


AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

log = logging.getLogger()

class AWSSigV4(httpx.Auth):
    """
    Automatically sign all requests sent by `httpx` library using `SigV4` as mandated by AWS for IAM gated services.
    By default we assume it's the OpenSearch service. Override `aws_service` accordingly to change this.

    Examples:
    ---------
    Sync:
    ```
    with httpx.Client(auth = AWSSigV4(), base_url = 'https://some-opensearch-domain.amazonaws.com') as http_session:
        resp: httpx.Response = http_session.get(url = 'some_indexname/_mapping')
        print(resp.json())
    ```

    Async:
    ```
    async with httpx.AsyncClient(
        auth = AWSSigV4(),
        base_url = 'https://some-opensearch-domain.amazonaws.com',
    ) as http_session:
        resp: httpx.Response = await http_session.get(url = 'some_indexname/_mapping')
        print(resp.json())
    ```
    """
    def __init__(self,
        aws_service: str = 'es',
        aws_region: str = AWS_REGION,
        aws_session_creds: Optional[Credentials] = None,
        log = log,
    ):
        self.aws_region = aws_region
        self.aws_service = aws_service
        self._aws_creds = aws_session_creds if aws_session_creds is not None else boto3.Session().get_credentials()
        if not isinstance(self._aws_creds, RefreshableCredentials) and not os.getenv('AWS_LAMBDA_FUNCTION_NAME'):
            log.warning((f'Expected `RefreshableCredentials` type! Found: {type(self._aws_creds)} instead. These will '
                          'not be automatically refreshed on session expiration and will hence cause authentication '
                          'errors in long running services.'))


    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, None, None]:
        """ Execute Authentication Flow. """
        aws_creds: ReadOnlyCredentials = self._aws_creds.get_frozen_credentials()
        aws_req = AWSRequest(method = request.method, url = str(request.url), data = request.content)
        sigv4 = SigV4Auth(credentials = aws_creds, service_name = self.aws_service, region_name = self.aws_region)
        sigv4.add_auth(aws_req)
        request.headers.update(dict(aws_req.headers))
        yield request
