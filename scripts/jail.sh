#!/bin/sh

COMMAND=
while getopts "dhilqvJ:u:U:cmrf:p:RJ:n:s:" "arg" ; do
	case "${arg}" in
		d|i|h|l|q|v|J|u|U|p|n|s|R)
			[ "${COMMAND}" ] && exit 1
			;;
		f)
			[ -r "${OPTARG}" ] || exit 1
			;;
		c|m|r)
			COMMAND="${arg}"
			;;
		*)
			break
			;;
	esac
	shift
done

exit 0
