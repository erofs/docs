# 🗺 Roadmap

Note that items marked with **\[GSoC\]** are also intended for Google Summer of
Code (GSoC) projects.

## Linux Kernel

 - [EROFS page cache sharing across different filesystems](https://lwn.net/Articles/984092);

 - [Preliminary EROFS Rust in-kernel adaption (EXPERIMENTAL, program for students)](https://lore.kernel.org/r/20240916135634.98554-1-toolmanp@tlmp.cc);

## Userspace tools (erofs-utils)

 - Stabilize liberofs APIs;

 - **\[GSoC\]** [Multi-threaded decompression](gsoc.md#multi_threaded_decompression);

 - Fanotify on-demand loading support (using fanotify pre-content hooks);

 - Rebuild improvements (including incremental updates [\[1\]](https://git.kernel.org/xiang/erofs-utils/c/7550a30c332c)).

## Containers

 - [(containerd) EROFS Support and Improvements](https://github.com/containerd/containerd/issues/11340);

 - [(Kata Containers) EROFS Snapshotter Support in Kata](https://github.com/kata-containers/kata-containers/issues/11163);

 - [(gVisor) EROFS Snapshotter Support](https://docs.google.com/document/d/1JBBIAqEPwJHGOqML9wcEyZhKicfo9pWZOkahn31AfPs).

## Miscellaneous items

 - **\[GSoC\]** [Porting EROFS to BSD Kernels](gsoc.md#porting-erofs-to-freebsd).
