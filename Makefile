docker-local:
	docker compose -f compose.yaml up --build -d

docker-remote:
	docker compose -f compose.prod.yaml up --build -d

docker-dev:
	docker rm -f sec-daily-app && docker build -t sec-daily . && docker run -d --name sec-daily-app -p 8000:8000 --restart unless-stopped sec-daily