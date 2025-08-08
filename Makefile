# these will speed up builds, for docker-compose >= 1.25
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

############################################## docker compose related targets ##############################################
all: compose-down compose-build compose-up

compose-build:
	docker compose build

compose-up:
	docker compose up -d

compose-down:
	docker compose down --remove-orphans

compose-test:
	docker compose run --rm --no-deps --entrypoint=pytest rest_server /code/tests

compose-logs:
	docker compose logs -f rest_server

compose-destroy:
	docker compose down -v --remove-orphans

compose-ps:
	docker compose ps

compose-reload-code:
	docker compose restart rest_server

install:
	poetry install --with dev

coverage:
	coverage run -m pytest --verbose --junit-xml ./reports/tests.xml
	coverage report
	coverage xml -o ./reports/coverage.xml

lint:
	pre-commit run --all-files
