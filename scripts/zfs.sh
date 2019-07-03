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
	local regex=${1}

	echo "${OPTARG}" | grep -qE "${regex}"
}

check_create()
{
	local args
	while getopts "puo:V:" "args" ; do
		case "${args}" in
			p|u)
				;;
			o)
				if ! check_value '^[^=]+=.+$' ; then
					return 1
				fi
				;;
			V)
				if ! check_value '^[0-9]+[kKmMgG]*$' ; then
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

check_list()
{
	local args

	while getopts "rd:Hpo:t:s:S:" "args" ; do
		case "${args}" in
			r|H|p)
				;;
			d)
				check_value "^[0-9]+$" || return 1
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
	check_dataset_name "$(eval echo "\${${OPTIND}}")"
}

case "${1}" in
	create|destroy|list)
		cmd=${1}
		shift
		"check_${cmd}" "${@}"
		exit "${?}"
		;;
	*)
		exit 1
		;;
esac
