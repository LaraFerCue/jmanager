#!/bin/sh

USER=${1:?A user is needed}
PERMISSIONS="create,clone,destroy,hold,mount,release,rename,snapshot,canmount"

SCRIPTS_PATH="${PWD}/scripts"
if ! [ "$(uname -o)" = "FreeBSD" ] ; then
	mkdir -p "${HOME}/bin"
	sed "s,%ZFSLIB_PATH%,${SCRIPTS_PATH}/zfslib,g" \
		"${SCRIPTS_PATH}/zfs.sh" > "${HOME}/bin/zfs"
	chmod a+x "${HOME}/bin/zfs"
	chmod -R a+x "${SCRIPTS_PATH}/zfslib/"
	exit 0
fi

ZPOOL_NAME=$(zpool list -H | awk '{print $1;}')
if ! [ "${ZPOOL_NAME}" ] ; then
	exit 0
fi

CREATE_TEST_DATASET=false
DELEGATE_TEST_DATESET=false

if ! zfs list -o name -H | grep "${ZPOOL_NAME}/jmanager_test" ; then
	CREATE_TEST_DATASET=true
	DELEGATE_TEST_DATESET=true
elif [ -z "$(zfs allow "${ZPOOL_NAME}/jmanager_test")" ] ; then
	DELEGATE_TEST_DATESET=true
fi

if ${CREATE_TEST_DATASET} ; then
	if [ "$(id -u)" -ne 0 ] ; then
		echo "root permissions are needed to create the dataset" >&2
		exit 1
	fi

	zfs create "${ZPOOL_NAME}/jmanager_test"
	DELEGATE_TEST_DATESET=true
fi

if ${DELEGATE_TEST_DATESET} ; then
	if [ "$(id -u)" -ne 0 ] ; then
		echo "root permissions are needed to delegate permissions to the dataset" >&2
		exit 1
	fi

	zfs umount "${ZPOOL_NAME}/jmanager_test"
	zfs allow -u "${USER}" "${PERMISSIONS}" "${ZPOOL_NAME}/jmanager_test"
	zfs allow -c "${PERMISSIONS}" "${ZPOOL_NAME}/jmanager_test"
	chown -R "${USER}" "/${ZPOOL_NAME}/jmanager_test"
	su - lara -c "/sbin/zfs mount ${ZPOOL_NAME}/jmanager_test"
	chown -R "${USER}" "/${ZPOOL_NAME}/jmanager_test"
fi
