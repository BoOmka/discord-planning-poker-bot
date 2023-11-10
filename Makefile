.PHONY:install
install:
	pip3 install pipenv
	pipenv install --deploy --ignore-pipfile

.PHONY:run
run:
	docker compose -f ./deploy/local/docker-compose.yml up

.PHONY:up
up:
	docker compose -f ./deploy/local/docker-compose.yml up -d

.PHONY:down
down:
	docker compose -f ./deploy/local/docker-compose.yml down

