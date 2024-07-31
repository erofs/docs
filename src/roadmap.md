# 🗺 Roadmap

## Linux Kernel

 - Enable large folio support for compressed data [\[1\]](https://lore.kernel.org/r/20240305091448.1384242-1-hsiangkao@linux.alibaba.com)
[\[2\]](https://lore.kernel.org/r/20240703120051.3653452-1-hsiangkao@linux.alibaba.com);

 - [EROFS page cache sharing across different filesystems](https://lwn.net/Articles/984092);

 - Intel QAT/IAA accelerator support;

 - Large logical cluster support for smaller compression indexes;

 - [Preliminary EROFS Rust in-kernel adaption (EXPERIMENTAL, program for students)](https://summer-ospp.ac.cn/org/prodetail/241920019);

 - File-backed mounts to replace "EROFS over fscache" for container images.

## Userspace tools (erofs-utils)

 - Multi-threaded decompression;

 - [Intel QAT/IAA accelerator support](https://git.kernel.org/xiang/erofs-utils/c/4bfa9ef57e78);

 - Large logical cluster support for smaller compression indexes;

 - Stabilize liberofs APIs;

 - Rebuild improvements (including incremental updates [\[1\]](https://git.kernel.org/xiang/erofs-utils/c/7550a30c332c)).
