#!/bin/sh

FILE=${1:?No playbook given}

if ! [ -r "${FILE}" ] ; then
	echo "${FILE} not found" >&2
	exit 1
fi
