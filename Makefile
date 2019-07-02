USER ?= lara


pre-test:
	scripts/zfs_init.sh ${USER}
test:
	pipenv run pytest --ignore='src/test/utils_fetch_pytest.py' --cov-report term --cov=src
