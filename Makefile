PY := python3
PIP := pip
ENV := env

run-frontend:
	cd quantify-ui && \
	npm install && \
	npm run dev

run-backend:
	. ${ENV}/bin/activate
	cd stock_forecaster && \
	${PY} manage.py runserver

setup-backend:
	${PY} -m venv ${ENV} && \
	cd stock_forecaster && \
	${PIP} install -r requirements.txt