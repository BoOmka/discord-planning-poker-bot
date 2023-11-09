.PHONY:up
up:
	docker compose -f ./docker-compose.yml up

.PHONY:down
down:
	docker compose -f ./docker-compose.yml down

