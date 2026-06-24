.PHONY: test validate lint security-scan deploy destroy local-demo run

NAMESPACE ?= sre-lab

test:
	python -m unittest discover -s tests

validate: test
	python synthetics/check_http.py --dry-run

lint: validate

security-scan:
	trivy config .

deploy:
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -
	kubectl apply -f kubernetes/

destroy:
	kubectl delete -f kubernetes/ --ignore-not-found=true

local-demo:
	docker compose up --build

run:
	python services/api/app.py
