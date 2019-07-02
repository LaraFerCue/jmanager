from enum import Enum


class Component(Enum):
    MANIFEST = "MANIFEST"
    BASE_DEBUG = "base-dbg"
    BASE = "base"
    DOC = "doc"
    KERNEL_DEBUG = "kernel-dbg"
    KERNEL = "kernel"
    LIB32_DEBUG = "lib32-dbg"
    LIB32 = "lib32"
    PORTS = "ports"
    SRC = "src"
    TESTS = "tests"
