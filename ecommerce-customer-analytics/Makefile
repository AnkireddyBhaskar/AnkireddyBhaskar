.PHONY: install analysis notebook test lint

install:
	pip install -r requirements.txt

analysis:
	cd src && python -m retail_analysis.pipeline

notebook:
	jupyter notebook notebooks/ecommerce_customer_analytics.ipynb

test:
	pytest -q

lint:
	ruff check . && ruff format --check .
