#!/bin/sh
# shellcheck disable=SC2039
# SC2039: local is defined in Bourne Shell and Bash

: "${ZFSLIB_PATH:?Error: ZFSLIB_PATH not set}"

# shellcheck source=zfslib/common.sh
. "${ZFSLIB_PATH}/common.sh"

option_in_list()
{
	local option=${1}
	local options_list="${2:-all}"
	local opt

	if [ "${options}" = "all" ] ; then
		return 0
	fi

	for opt in $(echo "${options_list}" | tr ',' ' ') ; do
		if [ "${option}" = "${opt}" ] ;then
			return 0
		fi
	done
	return 1
}

show_options()
{
	local options="${1:-all}"

	while read -r dataset _options; do
		for option in $(echo "${_options}" | tr ',' ' ') ; do
			value=$(echo "${option}" | awk -F '=' '{ print $2 }')
			option=$(echo "${option}" | awk -F '=' '{ print $1 }')

			if [ -z "${value}" ] || [ -z "${option}" ] ; then
				continue
			fi

			if option_in_list "${option}" "${options}" ; then
				printf "%s\t%s\t%s\n" "${dataset}" "${option}" "${value}"
			fi
		done
	done
}

depth=0
options=""
types=""
while getopts "rd:pHo:s:t:" "args" ; do
	case "${args}" in
		r)
			depth=-2
			;;
		d)
			if ! check_value '^[0-9]+$' ; then
				exit 1
			fi
			depth="${OPTARG}"
			;;
		H|p|o|s)
			;;
		t)
			if ! check_value "^((filesystem|snapshot|volume|all),?)+$" ; then
				exit 1
			fi
			if ! echo "${OPTARG}" | grep -q 'all' ; then
				types="^($(echo "${OPTARG}" | sed 's/,/|/g'))$"
			fi
			;;
		*)
			break
			;;
	esac
done

dataset_name="$(eval echo "\${${#}}")"
while [ "${OPTIND}" -gt 1 ] ; do
	: $((OPTIND -= 1))
	shift
done

while [ "${1}" ] ; do
	if [ "${1}" != "${dataset_name}" ] ; then
		options="${options} ${1}"
	fi
	shift
done
options=$(echo "${options}" | sed -e 's,^[[:space:]]*,,' -e 's,[[:space:]],|,g')

if ! check_dataset_name "${dataset_name}" ; then
	exit 1
fi

if [ -z "${options}" ] ; then
	exit 1
fi

get_entries "${dataset_name}" "${depth}" | grep -E "${types}" | \
	show_entries "1,7" | sed 's,;, ,g' |\
	show_options "${options}"

