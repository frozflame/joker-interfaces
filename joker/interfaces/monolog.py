#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import logging
from functools import cached_property
from json import JSONDecodeError
from urllib.parse import urljoin, urlparse

import requests
from volkanic.errors import TechnicalError

from joker.interfaces.http import ResponseDict

_logger = logging.getLogger(__name__)


class HTTPClient:
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

    @staticmethod
    def _log_bad_response(resp: requests.Response):
        _logger.error(
            'bad response: %s %r',
            resp.status_code, resp.content[:1000]
        )

    @classmethod
    def _decode_response(cls, resp: requests.Response):
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

    @classmethod
    def decode_response(cls, resp: requests.Response):
        try:
            return cls._decode_response(resp)
        except TechnicalError:
            cls._log_bad_response(resp)
            raise


class MonologInterface(HTTPClient):
    def fmt_url(self, channel: str):
        return urljoin(self.base_url, f'api/v1/{channel}')

    def add(self, channel: str, data: list):
        """Add data to the monolog server"""
        url = self.fmt_url(channel)
        _logger.info(
            'pushing %r records to monolog channel %r, %r',
            len(data), channel, url
        )
        resp = self.session.post(url, json=data)
        _logger.info(resp.text)

    def fetch(
            self,
            channel: str,
            since: str,
            limit: int = 1000,
            timeout: int = None) -> list[dict]:
        """Fetch data from the monolog server"""
        url = self.fmt_url(channel)
        _logger.info(
            'pulling %r records from monolog channel %r since %r, %r',
            limit, channel, since, url
        )
        params = {'since': since, 'limit': limit, 'timeout': timeout}
        params = {k: v for k, v in params.items() if v is not None}
        resp = self.session.get(url, params=params)
        return self.decode_response(resp)
