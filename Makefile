SET_USER ?= ${USER}


pre-test:
	scripts/zfs_init.sh ${SET_USER}
test: pre-test
	pipenv run pytest --cov-report html --cov=src --cov=models
