#!/bin/sh
# shellcheck disable=SC2039
# SC2039: local is defined in Bourne Shell and Bash

: "${ZFSLIB_PATH:?Error: ZFSLIB_PATH not set}"

# shellcheck source=zfslib/common.sh
. "${ZFSLIB_PATH}/common.sh"
options=""
zfs_type=filesystem
create_parents=false
while getopts "puo:V:" "args" ; do
	case "${args}" in
		p)
			create_parents=true
			;;
		u)
			;;
		o)
			if ! check_value '^[^=]+=.+$' ; then
				return 1
			fi
			if [ -z "${options}" ] ; then
				options="${OPTARG}"
			else
				options="${options},${OPTARG}"
			fi
			;;
		V)
			if ! check_value '^[0-9]+[kKmMgG]*$' ; then
				return 1
			fi
			if [ -z "${options}" ] ; then
				options="volsize=${OPTARG}"
			else
				options="${options},volsize=${OPTARG}"
			fi
			zfs_type=volume
			;;
		*)
			break
			;;
	esac
done
dataset_name="$(eval echo "\${${OPTIND}}")"
check_dataset_name "${dataset_name}"

grep -qE "^${dataset_name};" "${ZFS_TEST_DATABASE}" && return 1
if "${create_parents}" ; then
	create_recursive_datasets "${dataset_name}" "${zfs_type}" "${options}"
elif grep -qE "^$(get_parent_dataset "${dataset_name}")" "${ZFS_TEST_DATABASE}" ; then
	create_dataset "${dataset_name}" "${zfs_type}" "${options}"
else
	exit 1
fi
