"""
Setup file for the Project Summarizer project.
"""

import runpy

from setuptools import setup


def __parse_requirements():
    lineiter = (line.strip() for line in open("install-requirements.txt", "r"))
    return [line for line in lineiter if line and not line.startswith("#")]


def __get_semantic_version():
    version_meta = runpy.run_path("./project_summarizer/version.py")
    return version_meta["__version__"]


def __load_readme_file():
    with open("README.md", "r", encoding="utf-8") as readme_file:
        return readme_file.read()


AUTHOR = "Jack De Winter"
AUTHOR_EMAIL = "jack.de.winter@outlook.com"
PROJECT_URL = "https://github.com/jackdewinter/pyscan"
PROJECT_URLS = {
    "Change Log": "https://github.com/jackdewinter/pyscan/blob/main/changelog.md",
}

PACKAGE_NAME = "project_summarizer"
SEMANTIC_VERSION = __get_semantic_version()
MINIMUM_PYTHON_VERSION = "3.8.0"

ONE_LINE_DESCRIPTION = "TBD"
LONG_DESCRIPTION = __load_readme_file()
LONG_DESCRIPTION_CONTENT_TYPE = "text/markdown"

KEYWORDS = [""]
PROJECT_CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Natural Language :: English",
]

PACKAGE_MODULES = [
    "project_summarizer",
]

setup(
    name=PACKAGE_NAME,
    version=SEMANTIC_VERSION,
    python_requires=">=" + MINIMUM_PYTHON_VERSION,
    install_requires=__parse_requirements(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    url=PROJECT_URL,
    description=ONE_LINE_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    keywords=KEYWORDS,
    classifiers=PROJECT_CLASSIFIERS,
    project_urls=PROJECT_URLS,
    entry_points={
        "console_scripts": [
            "project_summarizer=project_summarizer.__main__:main",
        ],
    },
    packages=PACKAGE_MODULES,
    include_package_data=True,
)
