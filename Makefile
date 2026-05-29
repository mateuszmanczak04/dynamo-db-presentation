.PHONY: up down seed wipe logs

up:
	docker compose up --build -d

down:
	docker compose down -v

seed:
	curl -s -X POST http://localhost:8080/api/seed | jq

wipe:
	curl -s -X DELETE http://localhost:8080/api/seed | jq

logs:
	docker compose logs -f
