#!/bin/sh
# shellcheck disable=SC2039
# SC2039: local is defined in Bourne Shell and Bash

: "${ZFSLIB_PATH:?Error: ZFSLIB_PATH not set}"

# shellcheck source=zfslib/common.sh
. "${ZFSLIB_PATH}/common.sh"

create_recursive_snapshots()
{
	local dataset=${1}
	local snapshot_name=${2}
	local options=${3}

	for entry in $(get_entries "${dataset}" -2 | show_entries 1) ; do
		create_dataset "${entry}@${snapshot_name}" "snapshot" "${options}"
	done
}

recursive=false
while getopts "ro:" "args" ; do
	case "${args}" in
		o)
			if ! check_value '^[^=]+=.+$' ; then
				return 1
			fi
			if [ -z "${options}" ] ; then
				options="${OPTARG}"
			else
				options="${options},${OPTARG}"
			fi
			;;
		r)
			recursive=true
			;;
		*)
			break
			;;
	esac
done

snapshot_name="$(eval echo "\${${OPTIND}}")"
dataset_name=$(echo "${snapshot_name}" | awk -F '@' '{ print $1 }')
snapshot_name=${snapshot_name##${dataset_name}@}

check_dataset_name "${dataset_name}" || return 1
check_snapshot_name "${snapshot_name}" || return 1

grep -qE "^${dataset_name};" "${ZFS_TEST_DATABASE}" || \
	return 1

grep -qE "^${dataset_name}@${snapshot_name};.*;snapshot;" "${ZFS_TEST_DATABASE}" && \
	return 1

if ! "${recursive}" ; then
	create_dataset "${dataset_name}@${snapshot_name}" "snapshot" "${options}"
else
	create_recursive_snapshots "${dataset_name}" "${snapshot_name}" "${options}"
fi
exit 0
