#!/usr/bin/env python
# ----------------------------------------------------------------------- #
# Copyright 2021, Gregor von Laszewski                                    #
#                                                                         #
# Licensed under the Apache License, Version 2.0 (the "License"); you may #
# not use this file except in compliance with the License. You may obtain #
# a copy of the License at                                                #
#                                                                         #
# http://www.apache.org/licenses/LICENSE-2.0                              #
#                                                                         #
# Unless required by applicable law or agreed to in writing, software     #
# distributed under the License is distributed on an "AS IS" BASIS,       #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.#
# See the License for the specific language governing permissions and     #
# limitations under the License.                                          #
# ------------------------------------------------------------------------#

from setuptools import find_packages, setup
import io

def readfile(filename):
    with io.open(filename, encoding="utf-8") as stream:
        return stream.read().split()


requiers = """
jmespath
oyaml
""".split("\n")

version = readfile("VERSION")[0].strip()

with open('README.md') as f:
    long_description = f.read()



NAME = "yamldb"
DESCRIPTION = "A database with yaml files as backend"
AUTHOR = "Gregor von Laszewski"
AUTHOR_EMAIL = "laszewski@gmail.com"
URL = "https://github.com/cloudmesh/yamldb"


setup(
    name=NAME,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=version,
    license="Apache 2.0",
    url=URL,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Database",
        "Topic :: Database :: Database Engines/Servers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9"
    ],
    install_requires=requiers,
    tests_require=[
        "flake8",
        "coverage",
    ],
    zip_safe=False,
    python_requires=">=3.7",
)
