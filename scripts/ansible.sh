#!/bin/sh

: "${ANSIBLE_CONFIG:?No ansible configuration given}"

while [ "${1}" ] ;do
	case "${1}" in
		--inventory=*)
			argument=$(echo "${1}" | awk -F '=' '{ print $2 }')
			if ! [ -r "${argument}" ] ; then
				echo "${argument} is not readable" >&2
				exit 1
			fi
			;;
		--module-name=*)
			argument=$(echo "${1}" | awk -F '=' '{ print $2 }')
			if ! [ "${argument}" ] ; then
				echo "No module name given" >&2
				exit 1
			fi
			shift
			;;
		--args=*)
			argument=$(echo "${1}" | awk -F '=' '{ print $2 }')
			sh -nc "${argument}"
			;;
	esac
	shift
done
