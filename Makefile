USER ?= lara


pre-test:
	scripts/zfs_init.sh ${USER}
test:
	pipenv run pytest --cov-report term --cov=src
