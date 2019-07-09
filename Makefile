SET_USER?=		${USER}
JMANAGER_COMMAND=	python3.6 -m jmanager
JMANAGER_OPTIONS=	--jmanager-config src/test/resources/jmanager.conf

pre-test:
	scripts/zfs_init.sh ${SET_USER}
test: pre-test
	pipenv run pytest --cov-report html --cov=src --cov=models

test-commands: check-test-commands test-help

check-test-commands:
	if [ "$$(uname -o)" != "FreeBSD" ] ; then \
		echo "FreeBSD only!" >&2; \
		exit 1 ; \
	fi
	if [ "$$(id -u)" -ne 0 ] ; then \
		echo "Must be run as root!" >&2 ;\
		exit 1 ; \
	fi

test-help:
	python3.6 -m jmanager --help >> /dev/null
	python3.6 -m jmanager create --help >> /dev/null
	python3.6 -m jmanager destroy --help >> /dev/null
	python3.6 -m jmanager list --help >> /dev/null

test-create:
	${JMANAGER_COMMAND} ${JMANAGER_OPTIONS} \
		create --jmanagerfile examples/JManagerFile
	touch test-create

test-destroy: test-create
	${JMANAGER_COMMAND} ${JMANAGER_OPTIONS} \
		destroy example
