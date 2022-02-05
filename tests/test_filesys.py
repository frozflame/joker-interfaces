#!/usr/bin/env python3
# coding: utf-8

import hashlib

from joker.interfaces.filesys import Directory, MappedDirectory
from joker.interfaces.filesys import checksum


def assert_equal(a, b):
    assert a == b, (a, b)


def test_dir():
    d = Directory('/data/www/files')
    assert_equal(
        d.relative_to_base_dir('/data/www/files/js/v.js'),
        'js/v.js',
    )


def test_mapped_dir():
    md = MappedDirectory(
        '/data/www/files',
        'http://localhost/files'
    )
    assert_equal(
        md.join_url('img/1.jpg'),
        'http://localhost/files/img/1.jpg'
    )
    assert_equal(
        md.convert_local_path_to_url('/data/www/files/js/v.js'),
        'http://localhost/files/js/v.js',
    )
    assert_equal(
        md.convert_url_to_local_path('http://localhost/files/js/v.js'),
        '/data/www/files/js/v.js',
    )


def test_chksum():
    _nonhex_md5 = 'd41d8cd98f00b204e9800998ecf8427e'
    _nonhex_sha1 = 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
    chksum = checksum
    params = {
        'algo': 'md5',
        'length': 0,
    }
    assert chksum(__file__, **params).hexdigest() == _nonhex_md5

    params = {
        'algo': hashlib.md5(),
        'length': 0,
    }
    assert chksum(__file__, **params).hexdigest() == _nonhex_md5

    params = {
        'algo': hashlib.md5(),
        'length': -1,
        'offset': 2 ** 32,
    }
    assert chksum(__file__, **params).hexdigest() == _nonhex_md5

    params = {
        'algo': hashlib.md5(),
        'length': 10,
        'offset': 2 ** 32,
    }
    assert chksum(__file__, **params).hexdigest() == _nonhex_md5

    params = {
        'length': 10,
        'offset': 2 ** 32,
    }
    assert chksum(__file__, **params).hexdigest() == _nonhex_sha1


if __name__ == '__main__':
    test_chksum()


if __name__ == '__main__':
    test_multicheck()
