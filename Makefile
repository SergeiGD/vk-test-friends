test:
	-docker-compose run app coverage run manage.py test -v 2
	-docker-compose run app coverage report

run:
	docker-compose up

stop:
	docker-compose stop

doc:
	docker-compose run app python3 manage.py spectacular --color --file doc/openapi-auto.yml --validate
