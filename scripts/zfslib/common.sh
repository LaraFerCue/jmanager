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


