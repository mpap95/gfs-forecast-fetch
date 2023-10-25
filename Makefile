SHELL := /bin/bash

DOCKER_IMAGE_NAME := gfs-fetch

.PHONY: help
help: ## @HELP prints this message
help:
	@echo
	@echo 'Variables:'
	@echo '  DOCKER_IMAGE_NAME = $(DOCKER_IMAGE_NAME)'
	@echo
	@echo 'Usage:'
	@echo '  make <target>'
	@echo
	@echo 'Targets:'
	@grep -E '^.*: *## *@HELP' $(MAKEFILE_LIST)   \
	    | awk '                                   \
	        BEGIN {FS = ": *## *@HELP"};          \
	        { printf "  %-30s %s\n", $$1, $$2 };  \
	    ' | sort

.PHONY: pre-commit
pre-commit: ## @HELP runs pre-commit checks
pre-commit:
	@pre-commit run --all

.PHONY: docker-build
docker-build: ## @HELP builds Docker image
docker-build:
	@docker build . -t $(DOCKER_IMAGE_NAME)

.PHONY: docker-run
docker-run: ## @HELP runs the Docker image with the default arguments
docker-run:
	@docker run $(DOCKER_IMAGE_NAME) python /app/main.py --stdout=true
