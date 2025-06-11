pipenv run pyroma -q -n 10 .

rmdir /s /q dist
rmdir /s /q build
rmdir /s /q project_summarizer.egg-info

pipenv run python -m build

pipenv run twine check dist/*
