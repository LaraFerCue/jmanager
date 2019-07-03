#!/bin/sh
# shellcheck disable=SC2039
# SC2039: local is defined in Bourne Shell and Bash

check_dataset_name()
{
	if echo "${1}" | grep -qE '^-' ; then
		return 1
	fi
	return 0
}

check_value()
{
	local value=${1}
	local regex=${2}

	echo "${value}" | grep -qE "${regex}"
}

check_create()
{
	local args
	while getopts "puo:V:" "args" ; do
		echo "${args}"
		case "${args}" in
			p|u)
				;;
			o)
				if ! check_value "${OPTARG}" '^[^=]+=.+$' ; then
					return 1
				fi
				;;
			V)
				if ! check_value "${OPTARG}" '^[0-9]+[kKmMgG]*$' ; then
					return 1
				fi
				;;
			*)
				break
				;;
		esac
	done
	check_dataset_name "$(eval echo "\${${OPTIND}}")"
}

check_destroy()
{
	local args

	while getopts "fnpRrv" "args" ; do
		echo "${OPTIND}"
		case "${args}" in
			f|n|p|R|r|v)
				;;
			*)
				break
				;;
		esac
	done
	check_dataset_name "$(eval echo "\${${OPTIND}}")"
}

case "${1}" in
	create|destroy)
		cmd=${1}
		shift
		"check_${cmd}" "${@}"
		exit "${?}"
		;;
	*)
		exit 1
		;;
esac
