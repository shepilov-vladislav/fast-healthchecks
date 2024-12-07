.PHONY: help bash install-hooks update-uv lint test

# colors
GREEN = $(shell tput -Txterm setaf 2)
YELLOW = $(shell tput -Txterm setaf 3)
WHITE = $(shell tput -Txterm setaf 7)
RESET = $(shell tput -Txterm sgr0)
GRAY = $(shell tput -Txterm setaf 6)
TARGET_MAX_CHAR_NUM = 20

# Help

## Shows help.
help:
	@echo 'DEBUG_MODE: ${DEBUG_MODE}'
	@echo ''
	@echo 'Usage:'
	@echo ''
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			if (index(lastLine, "|") != 0) { \
				stage = substr(lastLine, index(lastLine, "|") + 1); \
				printf "\n ${GRAY}%s: \n\n", stage;  \
			} \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			if (index(lastLine, "|") != 0) { \
				helpMessage = substr(helpMessage, 0, index(helpMessage, "|")-1); \
			} \
			printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)
	@echo ''

.DEFAULT_GOAL := help

# Common

## Run bash environment | Common
bash:
	@source .venv/bin/activate

# Development

## Install pre-commit hooks. | Development
install-hooks:
	pre-commit install --hook-type pre-commit
	pre-commit install --hook-type commit-msg
	pre-commit install --install-hooks

## Update uv dependencies
update-uv:
	@uv sync --all-extras --upgrade

## Run linters
lint:
	@uv run pre-commit run --all-files

## Run tests
test:
	@uv run tox
	@rm *_report.xml

## Serve documentation locally
serve-docs:
	@uv run mkdocs serve
