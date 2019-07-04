#!/bin/sh
# shellcheck disable=SC2039
# SC2039: local is defined in Bourne Shell and Bash

export ZFS_TEST_DATABASE=/tmp/zfs_test_database.db

# We write the created datasets and the test dataset as CSV files
# using default values that are used in the test.
export ZFS_TEST_DATASET="zroot/jmanager_test"
export ZFS_ENTRY="%name%;90112;2147483648;90112;/%name%;%type%;"

check_dataset_name()
{
	if echo "${1}" | grep -qE '^-' ; then
		return 1
	fi
	return 0
}

check_value()
{
	local regex=${1}

	echo "${OPTARG}" | grep -qE "${regex}"
}

replace_wildcards()
{
	local expression=${1}
	local name=${2}
	local types=${3}

	echo "${expression}" | sed -e "s,%name%,${name},g" -e "s,%type%,${types},g"
}

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

get_entries()
{
	local dataset=${1:-""}
	local depth=${2:-0}

	if [ "${depth}" -eq -2 ] ; then
		grep -E "^${dataset}" "${ZFS_TEST_DATABASE}"
	elif [ "${depth}" -eq -1 ] ; then
		return 0
	else
		grep -E "^${dataset};" "${ZFS_TEST_DATABASE}"
		get_entries "${dataset}/[^/]+" "$((depth - 1))"
	fi
}

show_entries()
{
	local columns=${1:-1,2,3,4,5}
	local entry

	while read -r entry ; do
		echo "${entry}" | tr ';' '\t'
	done | cut -f "${columns}"
}
