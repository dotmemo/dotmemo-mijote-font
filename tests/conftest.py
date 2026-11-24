# SPDX-License-Identifier: MIT
from pathlib import Path

import pytest

from dotmemo_mijote.build import build


@pytest.fixture(scope="session")
def root():
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def built(root, tmp_path_factory):
    output = tmp_path_factory.mktemp("font-build")
    build(root, output)
    return output
