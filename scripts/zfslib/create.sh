#!/bin/sh
# shellcheck disable=SC2039
# SC2039: local is defined in Bourne Shell and Bash

set -x
ZFSLIB_PATH="$(realpath "$(dirname "${0}")")"

# shellcheck source=zfslib/common.sh
. "${ZFSLIB_PATH}/common.sh"

get_parent_dataset()
{
	local dataset=${1}

	echo "${dataset}" | awk -F '/' \
		'{ printf "%s", $1; for (i=2;i<NF;i++) printf "/%s", $i }'
}

create_recursive_datasets()
{
	local dataset=${1}
	local zfs_type=${2:-filesystem}
	local options=${3:-}
	local parent_dataset

	parent_dataset=$(get_parent_dataset "${dataset}")
	if ! grep -qE "^${parent_dataset};" "${ZFS_TEST_DATABASE}" ; then
		create_recursive_datasets "${parent_dataset}"
	fi
	create_dataset "${dataset}" "${zfs_type}" "${options}"
}

create_dataset()
{
	local dataset=${1}
	local zfs_type=${2:-filesystem}
	local options=${3:-}
	replace_wildcards "${ZFS_ENTRY}${options}" "${dataset}" "${zfs_type}"\
		>> "${ZFS_TEST_DATABASE}"
}

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
