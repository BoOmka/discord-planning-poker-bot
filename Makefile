.PHONY:up
up:
	docker compose -f ./deploy/local/docker-compose.yml up -d

.PHONY:down
down:
	docker compose -f ./deploy/local/docker-compose.yml down

