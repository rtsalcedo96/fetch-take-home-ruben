.PHONY: dependencies
pip-install:
	python -m ensurepip --upgrade && pip install -r requirements.txt

.PHONY: docker
start:
	docker-compose up -d
stop:
	docker-compose down --remove-orphans
clean:
	docker system prune -f
