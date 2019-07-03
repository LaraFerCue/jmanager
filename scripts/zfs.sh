#!/bin/sh
# shellcheck disable=SC2039
# SC2039: local is defined in Bourne Shell and Bash

# We write the created datasets and the test dataset as CSV files
# using default values that are used in the test.
ZFS_TEST_DATABASE=/tmp/zfs_test_database.db
ZFS_TEST_DATASET="zroot/jmanager_test"
ZFS_ENTRY="%name%;90112;2147483648;90112;/%name%;%type%;"

init_db()
{
	if ! [ -r "${ZFS_TEST_DATABASE}" ] ; then
		echo "${ZFS_ENTRY}" | sed \
			-e "s,%name%,${ZFS_TEST_DATASET},g" \
			-e "s,%type%,filesystem,g" >\
			"${ZFS_TEST_DATABASE}"
	fi
}

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

create()
{
	local args dataset_name options zfs_type

	options=""
	zfs_type=filesystem
	while getopts "puo:V:" "args" ; do
		case "${args}" in
			p|u)
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
	replace_wildcards "${ZFS_ENTRY}${options}" "${dataset_name}" \
		"${zfs_type}" >> "${ZFS_TEST_DATABASE}"
}

destroy()
{
	local args regex dry_run types dataset_name

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
}

show_entries()
{
	local entry

	while read -r entry ; do
		echo "${entry}" | tr ';' '\t'
	done
}

list()
{
	local args dataset_name regex depth zfs_type

	regex=""
	zfs_type="filesystem|volume|clone"
	while getopts "rd:Hpo:t:s:S:" "args" ; do
		case "${args}" in
			r)
				regex="^%name%.*;(%type%);"
				;;
			H|p)
				;;
			d)
				check_value "^[0-9]+$" || return 1

				depth="${OPTARG}"
				regex="^%name%"
				while [ "${depth}" -gt 0 ] ; do
					regex="${regex}/?[^/]*"
					: $((depth -= 1))
				done
				;;
			o)
				check_value "^[^,]+(,[^,]+)*$" || return 1
				;;
			t)
				check_value "^[^,]+(,[^,]+)*$" || return 1
				;;
			s|S)
				check_value "^[a-zA-Z]+$" || return 1
				;;
			*)
				break
				;;
		esac
	done
	dataset_name="$(eval echo "\${${OPTIND}}")"
	check_dataset_name "${dataset_name}"

	regex=$(replace_wildcards "${regex}" "${dataset_name}" "${zfs_type}")
	grep -E "${regex}" "${ZFS_TEST_DATABASE}" | show_entries
}

init_db
case "${1}" in
	create|destroy|list)
		cmd=${1}
		shift
		"${cmd}" "${@}"
		exit "${?}"
		;;
	*)
		exit 1
		;;
esac
