docker-local:
	docker compose -f compose.yaml up --build -d

docker-remote:
	docker compose -f compose.prod.yaml up --build -d

docker-db:
	docker compose -f compose.yaml up db -d
	docker compose -f compose.yaml logs db -f --tail 5

docker-dev:
	docker rm -f insider-daily-app && docker build -t insider-daily . && docker run -d --name insider-daily-app -p 8000:8000 --restart unless-stopped insider-daily

fast-dev:
	uv run --active uvicorn app.main:app --reload --port 8000

claude:
	claude --resume b0138809-de3f-43a7-8d49-32c038a6758c