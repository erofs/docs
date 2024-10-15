# 🗺 Roadmap

## Linux Kernel

 - [Enable large folio support for compressed data](https://git.kernel.org/torvalds/c/e080a26725fb);

 - [EROFS page cache sharing across different filesystems](https://lwn.net/Articles/984092);

 - [File-backed mounts to replace "EROFS over fscache" for container images](https://git.kernel.org/torvalds/c/69a3a0a45a2f);

 - Intel QAT/IAA accelerator support;

 - Large logical cluster support for smaller compression indexes;

 - [Preliminary EROFS Rust in-kernel adaption (EXPERIMENTAL, program for students)](https://summer-ospp.ac.cn/org/prodetail/241920019).

## Userspace tools (erofs-utils)

 - Multi-threaded decompression;

 - [Intel QAT/IAA accelerator support](https://git.kernel.org/xiang/erofs-utils/c/4bfa9ef57e78);

 - Large logical cluster support for smaller compression indexes;

 - Stabilize liberofs APIs;

 - Rebuild improvements (including incremental updates [\[1\]](https://git.kernel.org/xiang/erofs-utils/c/7550a30c332c)).
