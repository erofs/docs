# 🗺 Roadmap

## Linux Kernel

 - [Metadata compression](https://issues.redhat.com/browse/RHEL-75783);

 - [EROFS page cache sharing across different filesystems](https://lwn.net/Articles/984092);

 - [Preliminary EROFS Rust in-kernel adaption (EXPERIMENTAL, program for students)](https://summer-ospp.ac.cn/org/prodetail/241920019).

## Userspace tools (erofs-utils)

 - Metadata compression;

 - Stabilize liberofs APIs;

 - Multi-threaded decompression;

 - Rebuild improvements (including incremental updates [\[1\]](https://git.kernel.org/xiang/erofs-utils/c/7550a30c332c)).

## Containers

 - [(containerd) EROFS Support and Improvements](https://github.com/containerd/containerd/issues/11340);

 - [(Kata Containers) EROFS Snapshotter Support in Kata](https://github.com/kata-containers/kata-containers/issues/11163);

 - [(gVisor) EROFS Snapshotter Support](https://docs.google.com/document/d/1JBBIAqEPwJHGOqML9wcEyZhKicfo9pWZOkahn31AfPs).
