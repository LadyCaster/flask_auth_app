install-server:
	( \
		pip install virtualenv; \
		virtualenv venv; \
		source venv/bin/activate; \
		pip install -r requirements.txt; \
		python main.py db init; \
		python main.py db migrate; \
		python main.py db upgrade; \
	)

run-server:
	( \
		source ./venv/bin/activate; \
		python server/main.py runserver; \
	)

install-client:
	yarn install

run-client:
	yarn run start

build-client:
yarn run build