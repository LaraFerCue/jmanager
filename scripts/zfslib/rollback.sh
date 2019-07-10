#!/bin/sh
# shellcheck disable=SC2039
# SC2039: local is defined in Bourne Shell and Bash

: "${ZFSLIB_PATH:?Error: ZFSLIB_PATH not set}"

# shellcheck source=zfslib/common.sh
. "${ZFSLIB_PATH}/common.sh"


while getopts "rRf" "args" ; do
	case "${args}" in
		r|R|f)
			;;
		*)
			break
			;;
	esac
done

snapshot_name="$(eval echo "\${${OPTIND}}")"
dataset_name=$(echo "${snapshot_name}" | awk -F '@' '{ print $1 }')
snapshot_name=${snapshot_name##${dataset_name}@}

check_dataset_name "${dataset_name}" || return 1
check_snapshot_name "${snapshot_name}" || return 1

grep -qE "^${dataset_name}@${snapshot_name}" "${ZFS_TEST_DATABASE}"
