#!/usr/bin/env python
# encoding: UTF-8

import ast
import os.path

from setuptools import setup


try:
    # Includes bzr revision number
    from turberfield.ipc.about import version
except ImportError:
    try:
        # For setup.py install
        from turberfield.ipc import __version__ as version
    except ImportError:
        # For pip installations
        version = str(ast.literal_eval(
                    open(os.path.join(os.path.dirname(__file__),
                    "turberfield", "ipc", "__init__.py"),
                    'r').read().split("=")[-1].strip()))

__doc__ = open(os.path.join(os.path.dirname(__file__), "README.rst"),
               'r').read()

setup(
    name="turberfield-ipc",
    version=version,
    description="A Distributed Inter-Process Control Facility from the Turberfield project.",
    author="D Haynes",
    author_email="tundish@thuswise.org",
    url="https://www.assembla.com/spaces/turberfield/messages",
    long_description=__doc__,
    classifiers=[
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: GNU General Public License v3"
        " or later (GPLv3+)"
    ],
    namespace_packages=["turberfield"],
    packages=[
        "turberfield.ipc",
        "turberfield.ipc.demo",
        "turberfield.ipc.test",
    ],
    package_data={
        "turberfield.ipc": [
            "doc/*.rst",
            "doc/_templates/*.css",
            "doc/html/*.html",
            "doc/html/*.js",
            "doc/html/_sources/*",
            "doc/html/_static/css/*",
            "doc/html/_static/font/*",
            "doc/html/_static/js/*",
            "doc/html/_static/*.css",
            "doc/html/_static/*.gif",
            "doc/html/_static/*.js",
            "doc/html/_static/*.png",
            ],
    },
    install_requires=[
        "turberfield-utils>=0.32.0",
    ],
    extras_require={
        "demo": [
            "aiohttp>=2.2.0",
            "pyjwt>=1.5.2",
        ],
        "docbuild": [
            "babel<=1.3,>2.0",
            "sphinx-argparse>=0.1.15",
            "sphinxcontrib-seqdiag>=0.8.4",
        ],
    },
    tests_require=[],
    entry_points={
        "console_scripts": [],
        "turberfield.ipc.poa": [
            "udp = turberfield.ipc.policy:POA.UDP",
        ],
        "turberfield.ipc.role": [
            "rx = turberfield.ipc.policy:Role.RX",
            "tx = turberfield.ipc.policy:Role.TX",
        ],
        "turberfield.ipc.routing": [
            "application = turberfield.ipc.policy:Routing.Application",
        ]

    },
    zip_safe=False
)
