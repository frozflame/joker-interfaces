#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import json
import logging
import shlex
import traceback
import urllib.parse
from json import JSONDecodeError
from typing import Union
from urllib.parse import urljoin

import requests
from volkanic.errors import TechnicalError
from volkanic.introspect import razor

_logger = logging.getLogger(__name__)


class ResponseDict(dict):
    @property
    def code(self) -> int:
        return self.get('code', 3)

    @property
    def data(self):
        return self.get('data')

    @property
    def message(self):
        return self.get('message', 'OK')


def dump_json_request_to_curl(method: str, url: str, data=None, aslist=False):
    method = method.upper()
    if method == 'GET':
        parts = ['curl', url]
    else:
        parts = [
            'curl', '-X', method, url,
            '-H', 'Content-Type: application/json',
            '-d', json.dumps(razor(data), ensure_ascii=False),
        ]
    if aslist:
        return parts
    parts = [shlex.quote(s) for s in parts]
    return ' '.join(parts)


def _log_bad_response(resp: requests.Response):
    _logger.error(
        'bad response: %s %r',
        resp.status_code, resp.content[:1000]
    )


def _decode_response(resp: requests.Response):
    status = resp.status_code
    if status >= 400:
        raise TechnicalError(f'got response status code {status}')
    try:
        rd = ResponseDict(resp.json())
    except JSONDecodeError:
        raise TechnicalError('cannot decode json')
    if rd.code != 0:
        raise TechnicalError(f'error response ({rd.code})')
    return rd.data


def decode_response(resp: requests.Response):
    try:
        return _decode_response(resp)
    except TechnicalError:
        _log_bad_response(resp)
        raise


class HTTPClient:
    timeout = 30

    def __init__(self, base_url: str):
        self.base_url = base_url

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


HTTPService = HTTPClient


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


HTTPServiceInterface = HTTPClientInterface
