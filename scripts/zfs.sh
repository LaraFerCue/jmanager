#!/bin/sh

check_create()
{
	while [ "${1}" ] ; do
		case "${1}" in
			-p|-u)
				;;
			-o)
				if echo "${2}" | grep -qvE '^[^=]+=.+$' ; then
					return 1
				fi
				shift
				;;
			-V)
				if echo "${2}" | grep -qvE '^[0-9]+[kKmMgG]*$' ; then
					return 1
				fi
				shift
				;;
			*)
				break
				;;
		esac
		shift
	done

	if echo "${1}" | grep -qE '^-' ; then
		return 1
	fi
	return 0
}

case "${1}" in
	error)
		exit 1
       ;;
	create)
		shift
		check_create "${@}"
		exit "${?}"
		;;
	*)
		exit 0
		;;
esac
