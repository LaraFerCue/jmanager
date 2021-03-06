#!/bin/sh
# shellcheck disable=SC2039,SC2068
# SC2039: local is defined in Bourne Shell and Bash
# SC2068: the parameters should be passed to the real command

ZFSLIB_PATH="${PWD}/scripts/zfslib"

# shellcheck source=zfslib/common.sh
. "${ZFSLIB_PATH}/common.sh"

init_db()
{
	if ! [ -s "${ZFS_TEST_DATABASE}" ] ; then
		echo "${ZFS_ENTRY}" | sed \
			-e "s,%name%,${ZFS_TEST_DATASET},g" \
			-e "s,%type%,filesystem,g" >\
			"${ZFS_TEST_DATABASE}"
	fi
}


init_db

CMD=${1}
shift
if [ -x "${ZFSLIB_PATH}/${CMD}.sh" ] ; then
	export ZFSLIB_PATH
	"${ZFSLIB_PATH}/${CMD}.sh" ${@}
	exit "${?}"
else
	exit 1
fi
