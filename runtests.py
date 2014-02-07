#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytest
import sys

class MyPlugin:
    def pytest_sessionfinish(self):
        print("\n*** test run reporting finishing")


# Empty statement here needed so minversion reports no error
#pytest

pytest.main(plugins=[MyPlugin()] )

