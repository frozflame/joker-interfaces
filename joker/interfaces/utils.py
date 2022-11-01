#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import json
import logging
import shlex
from functools import cached_property
from json import JSONDecodeError
from urllib.parse import urlparse

import requests
# noinspection PyUnresolvedReferences
from joker.meta.utils import *
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
    if rd.message:
        _logger.info(rd.message)
    return rd.data


def decode_response(resp: requests.Response):
    try:
        return _decode_response(resp)
    except TechnicalError:
        _log_bad_response(resp)
        raise


class _BaseHTTPClient:
    @staticmethod
    def _check_url(url: str):
        path = urlparse(url).path
        if path == '' or path.endswith('/'):
            return
        raise ValueError('service url path must end with "/"')

    def __init__(self, url: str):
        self._check_url(url)
        self.base_url = url
        c = self.__class__.__name__
        _logger.info('new %s instance, %r', c, url)

    @cached_property
    def session(self):
        return requests.session()
