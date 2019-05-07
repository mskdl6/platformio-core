# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from platformio.project.config import ProjectConfig

BASE_CONFIG = """
[platformio]
env_default = esp32dev, lolin32
extra_configs =
  extra_envs.ini
  extra_debug.ini

[common]
debug_flags = -D RELEASE
lib_flags = -lc -lm
extra_flags = ${sysenv.__PIO_TEST_CNF_EXTRA_FLAGS}

[env:esp-wrover-kit]
platform = espressif32
framework = espidf
board = esp-wrover-kit
build_flags = ${common.debug_flags} ${common.extra_flags}
"""

EXTRA_ENVS_CONFIG = """
[env:esp32dev]
platform = espressif32
framework = espidf
board = esp32dev
build_flags = ${common.lib_flags} ${common.debug_flags}

[env:lolin32]
platform = espressif32
framework = espidf
board = lolin32
build_flags = ${common.debug_flags} ${common.extra_flags}
"""

EXTRA_DEBUG_CONFIG = """
# Override base "common.debug_flags"
[common]
debug_flags = -D DEBUG=1

[env:lolin32]
build_flags = -Og
"""


def test_parser(tmpdir):
    tmpdir.join("platformio.ini").write(BASE_CONFIG)
    tmpdir.join("extra_envs.ini").write(EXTRA_ENVS_CONFIG)
    tmpdir.join("extra_debug.ini").write(EXTRA_DEBUG_CONFIG)

    config = None
    with tmpdir.as_cwd():
        config = ProjectConfig(tmpdir.join("platformio.ini").strpath)
    assert config

    # sections
    assert config.sections() == [
        "platformio", "common", "env:esp-wrover-kit", "env:esp32dev",
        "env:lolin32"
    ]

    # sysenv
    assert config.get("common", "extra_flags") == ""
    os.environ["__PIO_TEST_CNF_EXTRA_FLAGS"] = "-L /usr/local/lib"
    assert config.get("common", "extra_flags") == "-L /usr/local/lib"

    # get
    assert config.get("common", "debug_flags") == "-D DEBUG=1"
    assert config.get("env:esp32dev", "build_flags") == "-lc -lm -D DEBUG=1"
    assert config.get("env:lolin32", "build_flags") == "-Og"
    assert config.get("env:esp-wrover-kit",
                      "build_flags") == ("-D DEBUG=1 -L /usr/local/lib")

    # items
    assert config.items("common") == [("debug_flags", "-D DEBUG=1"),
                                      ("lib_flags", "-lc -lm"),
                                      ("extra_flags", "-L /usr/local/lib")]
    assert config.items(env="esp32dev") == [("platform", "espressif32"),
                                            ("framework", "espidf"),
                                            ("board", "esp32dev"),
                                            ("build_flags",
                                             "-lc -lm -D DEBUG=1")]

    # envs
    assert config.envs() == ["esp-wrover-kit", "esp32dev", "lolin32"]
    assert config.default_envs() == ["esp32dev", "lolin32"]
