#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import json
import logging
import traceback
import urllib.parse
from typing import Union
from urllib.parse import urljoin

import requests

from joker.interfaces.utils import (
    ResponseDict, dump_json_request_to_curl, _log_bad_response,
    _decode_response, decode_response, _BaseHTTPClient,
)

_logger = logging.getLogger(__name__)

_compat_names = [
    decode_response,
    _decode_response,
    _log_bad_response,
    dump_json_request_to_curl,
    ResponseDict,
    _BaseHTTPClient,
]


class HTTPClient(_BaseHTTPClient):
    timeout = 30

    def get_url(self, path: str):
        return urllib.parse.urljoin(self.base_url, path)

    @staticmethod
    def _load_json(resp: requests.Response) -> Union[dict, list, None]:
        err = _logger.error
        if resp.status_code != 200:
            err('status_code %s from %s', resp.status_code, resp.url)
            return
        try:
            data = json.loads(resp.text)
        except json.JSONDecodeError:
            traceback.print_exc()
            err('bad json from %s', resp.url)
            return
        if not isinstance(data, dict):
            err('wrong response type (%s) from %s', type(data), resp.url)
        code = data.get('code')
        if data.get('code'):
            err('non-zero code (%s) from %s', code, resp.url)
            return
        return data

    @staticmethod
    def log_request_as_curl(
            method: str, url: str, data=None, level=logging.DEBUG):
        if not _logger.isEnabledFor(level):
            return
        cmd = dump_json_request_to_curl(method, url, data=data)
        _logger.log(level, cmd)

    @staticmethod
    def log_resp_content(
            resp: requests.Response, level=logging.ERROR):
        if not _logger.isEnabledFor(level):
            return
        try:
            _logger.log(level, resp.text[:255])
        except Exception:
            _logger.log(level, resp.content[:255])
            traceback.print_exc()

    def json_request(self, method, path, data=None, **kwargs) \
            -> Union[dict, list, None]:
        url = self.get_url(path)
        method = method.upper()
        kwargs.setdefault('timeout', self.timeout)
        if data is not None:
            kwargs['data'] = json.dumps(data, default=str)
            kwargs['headers'] = {'Content-type': 'application/json'}
        resp = requests.request(method, url, **kwargs)
        resp_data = self._load_json(resp)
        if resp_data is None:
            self.log_resp_content(resp)
            self.log_request_as_curl(method, url, data)
            return
        self.log_request_as_curl(method, url, data, level=logging.DEBUG)
        return resp_data

    def json_get(self, path, **kwargs) -> Union[dict, list, None]:
        assert 'data' not in kwargs
        return self.json_request('GET', path, **kwargs)

    def json_post(self, path, data=None, **kwargs) -> Union[dict, list, None]:
        assert 'data' not in kwargs
        return self.json_request('POST', path, data=data, **kwargs)


# will be removed in 0.2.0
HTTPService = HTTPClient


# deprecated; will be removed in 0.2.0
class HTTPClientInterface:
    def __init__(self, config: dict):
        self._upstream_config = config

    def __getitem__(self, service_name: str) -> HTTPService:
        return HTTPService(self._upstream_config[service_name])

    def get_service_url(self, service_name: str, path: str = None):
        base_url = self._upstream_config[service_name]
        if not path:
            return base_url
        return urljoin(base_url, path)


# deprecated; will be removed in 0.2.0
HTTPServiceInterface = HTTPClientInterface
