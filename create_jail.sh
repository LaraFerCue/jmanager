#!/bin/sh -eu

: "${FREEBSD_VERSION:=$(uname -r)}"
: "${ARCH:=$(uname -m)}"
: "${JAIL_PATH:=/usr/jails}"
: "${ZPOOL_NAME:=zroot}"
: "${JAIL_NAME:?Please specify JAIL_NAME}"

: "${PREFIX:=${PWD}}"

FTP_URL=ftp://ftp.FreeBSD.org/pub/FreeBSD/releases

fetch -o /tmp/base.txz "${FTP_URL}/${ARCH}/${FREEBSD_VERSION}/base.txz"

zfs list "${ZPOOL_NAME}${JAIL_PATH}" >/dev/null 2>/dev/null ||\
	zfs create "${ZPOOL_NAME}${JAIL_PATH}"

zfs list "${ZPOOL_NAME}${JAIL_PATH}/${JAIL_NAME}" >/dev/null 2>/dev/null ||\
	zfs create "${ZPOOL_NAME}${JAIL_PATH}/${JAIL_NAME}"

tar -x -v -f /tmp/base.txz -C "${JAIL_PATH}/${JAIL_NAME}"
sed "s,%name%,${JAIL_NAME},g" "${PREFIX}/jail.conf.template" > \
	"${PREFIX}/${JAIL_NAME}_jail.conf"
