# 🗺 Roadmap

## Linux Kernel

 - [EROFS page cache sharing across different filesystems](https://lwn.net/Articles/984092);

 - Intel QAT/IAA accelerator support;

 - Large logical cluster support for smaller compression indexes;

 - [Preliminary EROFS Rust in-kernel adaption (EXPERIMENTAL, program for students)](https://summer-ospp.ac.cn/org/prodetail/241920019).

## Userspace tools (erofs-utils)

 - Multi-threaded decompression;

 - [Fragment cache to speed up (fsck.erofs) image extraction and erofsfuse](https://lore.kernel.org/r/20231023071528.1912105-1-lyy0627@sjtu.edu.cn);

 - [Intel QAT/IAA accelerator support](https://git.kernel.org/xiang/erofs-utils/c/4bfa9ef57e78);

 - Stabilize liberofs APIs;

 - Rebuild improvements (including incremental updates [\[1\]](https://git.kernel.org/xiang/erofs-utils/c/7550a30c332c)).
