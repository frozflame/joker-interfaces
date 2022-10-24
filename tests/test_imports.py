#!/usr/bin/env python3
# coding: utf-8

import importlib

import joker.meta
from volkanic.introspect import find_all_plain_modules


class JokerInterface(joker.meta.JokerInterface):
    package_name = 'joker.interfaces'


ji = JokerInterface()


def test_module_imports():
    for dotpath in find_all_plain_modules(ji.under_project_dir()):
        if dotpath.startswith('joker.'):
            print(dotpath)
            importlib.import_module(dotpath)


if __name__ == '__main__':
    test_module_imports()
