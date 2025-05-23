"""
Setup file for the Project Summarizer project.
"""

import runpy

from setuptools import setup


def __parse_requirements():
    with open("install-requirements.txt", "r", encoding="utf-8") as requirement_file:
        lineiter = [line.strip() for line in requirement_file]
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
    "Change Log": "https://project-summarizer.readthedocs.io/en/latest/changelog/",
}

PACKAGE_NAME = "project_summarizer"
SEMANTIC_VERSION = __get_semantic_version()
MINIMUM_PYTHON_VERSION = "3.9.0"

ONE_LINE_DESCRIPTION = (
    "A simple tool for summarizing information about the current project."
)
LONG_DESCRIPTION = __load_readme_file()
LONG_DESCRIPTION_CONTENT_TYPE = "text/markdown"

KEYWORDS = ["project", "tool", "coverage", "pytest"]
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
    "project_summarizer.plugin_manager",
    "project_summarizer.plugins",
]

setup(
    name=PACKAGE_NAME,
    version=SEMANTIC_VERSION,
    python_requires=f">={MINIMUM_PYTHON_VERSION}",
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
