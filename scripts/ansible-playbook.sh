#!/bin/sh

while [ "${1}" ] ; do
    case "${1}" in
        --inventory=*)
        ;;
        *)
        break
        ;;
    esac
    shift
done

FILE=${1:?No playbook given}

if ! [ -r "${FILE}" ] ; then
	echo "${FILE} not found" >&2
	exit 1
fi
