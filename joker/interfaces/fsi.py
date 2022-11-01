#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import os
import typing
import urllib.parse
import zipfile
from dataclasses import dataclass
from functools import cached_property

import requests

PathLike = typing.Union[str, os.PathLike]


class MemberFile(typing.TypedDict):
    cid: str
    filename: str


@dataclass
class FileStorageInterface:
    base_url: str
    credential: dict

    @cached_property
    def session(self):
        sess = requests.session()
        url = urllib.parse.urljoin(self.base_url, '/login')
        sess.post(url, data=self.credential)
        return sess

    def save(self, content: bytes) -> str:
        url = urllib.parse.urljoin(self.base_url, '/files')
        resp = self.session.post(url, files={'file': content})
        return resp.json()['data']

    def load(self, cid: str) -> bytes:
        url = urllib.parse.urljoin(self.base_url, f'/files/{cid}')
        resp = requests.get(url)
        return resp.content

    def create_archive(self, path: PathLike, memberfiles: list[MemberFile]):
        with zipfile.ZipFile(path, "w") as zipf:
            for m in memberfiles:
                content = self.load(m['cid'])
                with zipf.open(m['filename'], 'w') as fout:
                    fout.write(content)
