#!/bin/sh
# shellcheck disable=SC2039
# SC2039: local is defined in Bourne Shell and Bash

: "${ZFSLIB_PATH:?Error: ZFSLIB_PATH not set}"

# shellcheck source=zfslib/common.sh
. "${ZFSLIB_PATH}/common.sh"

types=""
dry_run=false
while getopts "dfnpRrv" "args" ; do
	case "${args}" in
		d|f|p|v)
			;;
		r)
			types="filesystem|snapshot"
			;;
		R)
			types="filesystem|volume|bookmark|clone|snapshot"
			;;
		n)
			dry_run=true
			;;
		*)
			break
			;;
	esac
done
dataset_name="$(eval echo "\${${OPTIND}}")"
check_dataset_name "${dataset_name}"

grep -qE "^${dataset_name};" "${ZFS_TEST_DATABASE}" || return 1
if ! "${dry_run}" ; then
	if [ -z "${types}" ] ;then
		grep -vE "^${dataset_name};" "${ZFS_TEST_DATABASE}" \
			> "${ZFS_TEST_DATABASE}.tmp"
	else
		grep -vE "^${dataset_name}" "${ZFS_TEST_DATABASE}" |\
			grep -vE ";(${types});" \
			> "${ZFS_TEST_DATABASE}.tmp"
	fi
	mv "${ZFS_TEST_DATABASE}.tmp" "${ZFS_TEST_DATABASE}"
fi

