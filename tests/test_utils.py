#!/usr/bin/env python3
# coding: utf-8


from joker.interfaces import utils


def test_multicheck():
    assert utils.check_inclusive_prefixes('hello-world', ['good', 'hello'])
    assert not utils.check_inclusive_prefixes('hello-world', ['bad', 'ello'])
    assert not utils.check_inclusive_prefixes('hello-world', [])
    assert utils.check_exclusive_prefixes('hello-world', ['world', 'ello'])
    assert utils.check_exclusive_prefixes('hello-world', [])
    assert not utils.check_exclusive_prefixes('hello-world', ['hello', 'ello'])

