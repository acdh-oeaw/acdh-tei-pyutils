#!/usr/bin/env python

"""The setup script."""

import os
import acdh_tei_pyutils as module
from setuptools import setup, find_packages


def walker(base, *paths):
    file_list = set([])
    cur_dir = os.path.abspath(os.curdir)

    os.chdir(base)
    try:
        for path in paths:
            for dname, dirs, files in os.walk(path):
                for f in files:
                    file_list.add(os.path.join(dname, f))
    finally:
        os.chdir(cur_dir)

    return list(file_list)


with open("README.md") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("requirements_dev.txt") as f:
    dev_requirements = f.read().splitlines()

setup(
    author="Peter Andorfer, Daniel Stoxreiter",
    author_email="peter.andorfer@oeaw.ac.at",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Utilty functions to work with TEI Documents",
    entry_points={
        "console_scripts": [
            "add-attributes=acdh_tei_pyutils.cli:add_base_id_next_prev",
            "mentions-to-indices=acdh_tei_pyutils.cli:mentions_to_indices",
            "denormalize-indices=acdh_tei_pyutils.cli:denormalize_indices",
            "add-handles=acdh_tei_pyutils.cli:add_handles",
            "schnitzler=acdh_tei_pyutils.cli:schnitzler",
        ],
    },
    install_requires=requirements,
    license="MIT",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="acdh-tei-pyutils",
    name="acdh-tei-pyutils",
    packages=find_packages(include=["acdh_tei_pyutils", "acdh_tei_pyutils.*"]),
    package_data={
        module.__name__: walker(os.path.dirname(module.__file__), "files"),
    },
    setup_requires=dev_requirements,
    test_suite="tests",
    tests_require=dev_requirements,
    url="https://github.com/acdh-oeaw/acdh-tei-pyutils",
    version="v1.6",
    zip_safe=False,
)
