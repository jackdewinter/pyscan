rmdir /s /q dist
rmdir /s /q build
rmdir /s /q project_summarizer.egg-info

pipenv run python setup.py sdist bdist_wheel

pipenv run twine check dist/*
