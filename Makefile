SET_USER?=		${USER}
JMANAGER_COMMAND=	python3.6 -m jmanager
JMANAGER_OPTIONS=	--jmanager-config src/test/resources/jmanager.conf

COVERAGE_FOLDERS=	jmanager/factories \
			jmanager/models \
			jmanager/utils \
			test

LIST_TYPE=jail

.PHONY: pre-test
pre-test:
	scripts/zfs_init.sh ${SET_USER}

.PHONY: test
test: pre-test
	for folder in ${COVERAGE_FOLDERS} ; do \
		echo "--cov=$${folder}" ; \
	done | xargs pipenv run pytest --cov-report html

.PHONY: test_commands
test_commands: test_help test_create test_destroy

.PHONY: check_test_commands
check_test_commands:
	if [ "$$(uname -o)" != "FreeBSD" ] ; then \
		echo "FreeBSD only!" >&2; \
		exit 1 ; \
	fi
	if [ "$$(id -u)" -ne 0 ] ; then \
		echo "Must be run as root!" >&2 ;\
		exit 1 ; \
	fi

.PHONY: test_help
test_help:
	python3.6 -m jmanager --help >> /dev/null
	python3.6 -m jmanager create --help >> /dev/null
	python3.6 -m jmanager destroy --help >> /dev/null
	python3.6 -m jmanager list --help >> /dev/null

.PHONY: test_create
test_create: check_test_commands
	${JMANAGER_COMMAND} ${JMANAGER_OPTIONS} \
		create examples/JManagerFile

.PHONY: test_destroy
test_destroy: check_test_commands test_create
	${JMANAGER_COMMAND} ${JMANAGER_OPTIONS} \
		destroy example

.PHONY: test_list
test_list:
	${JMANAGER_COMMAND} ${JMANAGER_OPTIONS} \
		list --type ${LIST_TYPE}
