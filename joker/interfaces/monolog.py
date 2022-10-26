#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import logging
from urllib.parse import urljoin

from joker.interfaces.http import (
    _BaseHTTPClient, decode_response
)

_logger = logging.getLogger(__name__)


class MonologInterface(_BaseHTTPClient):
    def fmt_url(self, channel: str):
        return urljoin(self.base_url, f'api/v1/{channel}')

    def push(self, channel: str, data: list):
        """Push data to the monolog server"""
        url = self.fmt_url(channel)
        _logger.info(
            'pushing %r records to monolog channel %r, %r',
            len(data), channel, url
        )
        resp = self.session.post(url, json=data)
        _logger.info(resp.text)

    def pull(
            self,
            channel: str,
            since: str,
            limit: int = 1000,
            timeout: int = None) -> list[dict]:
        """Pull data from the monolog server"""
        url = self.fmt_url(channel)
        _logger.info(
            'pulling %r records from monolog channel %r since %r, %r',
            limit, channel, since, url
        )
        params = {'since': since, 'limit': limit, 'timeout': timeout}
        params = {k: v for k, v in params.items() if v is not None}
        resp = self.session.get(url, params=params)
        return decode_response(resp)

    add = push
    fetch = pull
