#!/bin/sh -x
# shellcheck disable=SC2039
# SC2039: local is defined in Bourne Shell and Bash

: "${ZFSLIB_PATH:?Error: ZFSLIB_PATH not set}"

# shellcheck source=zfslib/common.sh
. "${ZFSLIB_PATH}/common.sh"

set -x
create_parents=false
options=""
while getopts "po:" "args" ; do
	case "${args}" in
		p)
			create_parents=true
			;;
		o)
			if ! check_value '^[^=]+=.+$' ; then
				return 1
			fi
			options="${options},${OPTARG}"
			;;
		*)
			break
			;;
	esac
done

dataset_name="$(eval echo "\${${OPTIND}}")"
snapshot_name=$(echo "${dataset_name}" | awk -F '@' '{ print $2 }')
dataset_name=${dataset_name%%@${snapshot_name}}

options="origin=${dataset_name}@${snapshot_name}${options}"
echo "${snapshot_name}" | grep -qE '^[a-zA-Z0-9_-]+$' || exit 1
shift
clone_name="$(eval echo "\${${OPTIND}}")"
check_dataset_name "${dataset_name}" || exit 1

grep -qE "^${clone_name};" "${ZFS_TEST_DATABASE}" && return 1
grep -qE "^${dataset_name}@${snapshot_name};" "${ZFS_TEST_DATABASE}" || return 1
if "${create_parents}" ; then
	create_recursive_datasets "${clone_name}" "clone" "${options}"
elif grep -qE "^$(get_parent_dataset "${clone_name}")" "${ZFS_TEST_DATABASE}" ; then
	create_dataset "${clone_name}" "clone" "${options}"
else
	exit 1
fi
