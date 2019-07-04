#!/bin/sh
# shellcheck disable=SC2039
# SC2039: local is defined in Bourne Shell and Bash

set -x
ZFSLIB_PATH="$(realpath "$(dirname "${0}")")"

# shellcheck source=zfslib/common.sh
. "${ZFSLIB_PATH}/common.sh"

show_entries()
{
	local entry

	while read -r entry ; do
		echo "${entry}" | tr ';' '\t'
	done
}

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


