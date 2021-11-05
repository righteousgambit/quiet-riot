SHELL:=/bin/bash

PROJECT := quiet-riot
PROJECT_UNDERSCORE := quiet_riot

# ---------------------------------------------------------------------------------------------------------------------
# Environment setup and management
# ---------------------------------------------------------------------------------------------------------------------
setup-env:
	python3 -m venv ./venv && source venv/bin/activate
	python3 -m pip install -r requirements.txt
setup-dev: setup-env
	echo "" && source venv/bin/activate
	python3 -m pip install -r requirements-dev.txt
clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '*.egg-link' -delete
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
# ---------------------------------------------------------------------------------------------------------------------
# ReadTheDocs
# ---------------------------------------------------------------------------------------------------------------------
uninstall-dev:
	python3 -m pip uninstall -r requirements-dev.txt -y
setup-docs-dependencies: uninstall-dev
	python3 -m pip install -r docs/requirements-docs.txt
build-docs: setup-docs-dependencies
	mkdocs build
serve-docs: setup-docs-dependencies
	mkdocs serve --dev-addr "127.0.0.1:8001"
# ---------------------------------------------------------------------------------------------------------------------
# Package building and publishing
# ---------------------------------------------------------------------------------------------------------------------
build: clean setup-env update-submodule
	python3 -m pip install --upgrade setuptools wheel
	python3 -m setup -q sdist bdist_wheel
install: build
	python3 -m pip install -q ./dist/${PROJECT}*.tar.gz
	${PROJECT} --help
uninstall:
	python3 -m pip uninstall ${PROJECT} -y
	python3 -m pip uninstall -r requirements.txt -y
	python3 -m pip uninstall -r requirements-dev.txt -y
	python3 -m pip freeze | xargs python3 -m pip uninstall -y
publish: build
	python3 -m pip install --upgrade twine
	python3 -m twine upload dist/*
	python3 -m pip install ${PROJECT}
# ---------------------------------------------------------------------------------------------------------------------
# Python Testing
# ---------------------------------------------------------------------------------------------------------------------
test: setup-dev
	python3 -m coverage run -m pytest -v
security-test: setup-dev
	bandit -r ./${PROJECT_UNDERSCORE}/
# ---------------------------------------------------------------------------------------------------------------------
# Linting and formatting
# ---------------------------------------------------------------------------------------------------------------------
fmt: setup-dev
	black ${PROJECT_UNDERSCORE}/
lint: setup-dev
	pylint ${PROJECT_UNDERSCORE}/
# ---------------------------------------------------------------------------------------------------------------------
# Miscellaneous development
# ---------------------------------------------------------------------------------------------------------------------
count-loc:
	echo "If you don't have tokei installed, you can install it with 'brew install tokei'"
	echo "Website: https://github.com/XAMPPRocky/tokei#installation'"
	tokei ./* --exclude --exclude '**/*.html' --exclude '**/*.json' --exclude results --exclude quiet_riot/shared/data/ --exclude tmp --exclude venv
github-actions-test:
	act -l
	# Run the CI job
	act -j ci

# ---------------------------------------------------------------------------------------------------------------------
# Integration tests
# 	Note: This will require that you actually create some credentials and use them.
# 	Not sure how we'd do this safely within a CI pipeline lol.
# 	but at least this is a good way of testing it locally and stashing the commands.
# ---------------------------------------------------------------------------------------------------------------------
test-help:
	./quiet_riot/bin/cli.py --help
infra-create:
	./quiet_riot/bin/cli.py infra create
infra-destroy:
	./quiet_riot/bin/cli.py infra destroy
footprint:
	./quiet_riot/bin/cli.py footprint -a 464622532012
enum-roles:

	./quiet_riot/bin/cli.py footprint -a 464622532012
