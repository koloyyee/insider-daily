docker-local:
	docker compose -f compose.yaml up --build -d

docker-remote:
	docker compose -f compose.prod.yaml up --build -d
