PY := python3
PIP := pip

run-frontend:
	cd quantify-ui && \
	npm install && \
	npm run dev

run-backend:
	cd stock_forecaster && \
	${PY} manage.py runserver

setup-backend:
	${PY} -m venv env && \
	cd stock_forecaster && \
	${PIP} install -r requirements.txt
