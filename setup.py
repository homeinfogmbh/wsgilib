#! /usr/bin/env python3
"""Installation script"""

from setuptools import setup

setup(
    name="wsgilib",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    install_requires=["flask", "werkzeug", "mimeutil"],
    author="HOMEINFO - Digitale Informationssysteme GmbH",
    author_email="<info@homeinfo.de>",
    maintainer="Richard Neumann",
    maintainer_email="<r.neumann@homeinfo.de>",
    packages=["wsgilib"],
    license="GPLv3",
    description="W WSGI framework extending flask.",
)
