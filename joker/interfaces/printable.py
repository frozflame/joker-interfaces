#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import json
import logging
import urllib.parse

import requests

from joker.interfaces.utils import _BaseHTTPClient

_logger = logging.getLogger(__name__)


class PDFClient(_BaseHTTPClient):
    def _generate(self, tpl_path: str, data: dict) -> (bytes, str):
        url = urllib.parse.urljoin(self.base_url, tpl_path)
        headers = {'Content-type': 'application/json'}
        payload = json.dumps(data, default=str)
        _logger.info('initial url: %s', url)
        resp = requests.post(url, data=payload, headers=headers)
        _logger.info('redirected url:', resp.url)
        return resp.content, resp.url

    def generate(self, tpl_path: str, data: dict) -> bytes:
        return self._generate(tpl_path, data)[0]
