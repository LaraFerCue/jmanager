#!/bin/sh
# shellcheck disable=SC2039
# SC2039: local is defined in Bourne Shell and Bash

set -x
: "${ZFSLIB_PATH:?Error: ZFSLIB_PATH not set}"

# shellcheck source=zfslib/common.sh
. "${ZFSLIB_PATH}/common.sh"

ZFS_TYPES="filesystem|snapshot|snap|volume|bookmark|all"
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
	done | cut -w -f "${columns}"
}

filter_entries()
{
	local types=${1}

	grep -E ";(${types});"
}

get_options()
{
	local options option_index

	options=""
	for option in $(echo "${OPTARG}" | tr ',' ' '); do
		option_index=0
		case "${option}" in
			name)
				option_index=1
				;;
			used)
				option_index=2
				;;
			avail)
				option_index=3
				;;
			refer)
				option_index=4
				;;
			mountpoint)
				option_index=5
				;;
			type)
				option_index=6
				;;
		esac
		[ "${option_index}" -eq 0 ] && continue
		if [ "${options}" ] ; then
			options="${options},${option_index}"
		else
			options="${option_index}"
		fi
	done

	echo "${options}"
}

depth=0
columns="1,2,3,4,5"
types=".*"
while getopts "rd:Hpo:t:s:S:" "args" ; do
	case "${args}" in
		r)
			depth=-2
			;;
		H|p)
			;;
		d)
			check_value "^[0-9]+$" || return 1

			depth="${OPTARG}"
			;;
		o)
			check_value "^[^,]+(,[^,]+)*$" || return 1
			columns="$(get_options)"
			;;
		t)
			check_value "^(${ZFS_TYPES}),?(${ZFS_TYPES})*$" || return 1
			types=$(echo "${OPTARG}" | sed 's/,/|/g')
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

get_entries "${dataset_name}" "${depth}" | filter_entries "${types}" | \
	show_entries "${columns}"


