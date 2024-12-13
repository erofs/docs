# 🙋 Frequently Asked Questions

## Why are images packaged in EROFS larger than those with SquashFS?

First of all, the initial target use cases of EROFS are _high-performance
embedded scenarios, such as smartphones powered by Android_.  Runtime
performance is always the top priority for EROFS (or, systems and applications
will be lagged), even if it means sacrificing some ultra-space savings to avoid
significant performance regressions against uncompressed approaches.

However, EROFS has landed **several new ondisk features** to narrow the slight
size difference with SquashFS.  When comparing, please ensure the same
configuration is used:

 - **Compression algorithm (if data is compressed)**: EROFS uses *LZ4* by
   default due to lowest decompression latencies among popular open-source
   algorithms, while SquashFS uses *GZIP* instead;

 - **Compressed extent size**: Almost all filesystems that natively support
   compression typically cut data into compressed extents for random access.
   EROFS focuses on smaller physical clusters to maximize random performance and
   use *block-sized physical clusters* by default (usually 4 KiB), whileas
   SquashFS uses *128 KiB*.  It can be adjusted using the `-C` option with
   `mkfs.erofs`.

:::{note}

Large physical clusters (e.g., 1MiB) can significantly degrade random read
performance as well as increase memory usage.  Please conduct a thorough
evaluation by factoring in the target image size prior to deployment.

:::

 - **Compression level**: For example, EROFS uses *LZ4HC_CLEVEL_DEFAULT (level 9)*
   for LZ4 HC, whereas SquashFS often uses
   *[LZ4HC_CLEVEL_MAX (level 12)](https://github.com/plougher/squashfs-tools/blob/4.6.1/squashfs-tools/lz4_wrapper.c#L52)*;

 - **Advanced features**: Enable the `-Efragments` option for EROFS when
   comparing with SquashFS.

In addition, EROFS may produce larger images due to the following differences:
 - **Inode size**: Currently EROFS has to use 64-byte ondisk inodes (extended
   inodes) to support per-inode nanosecond timestamps, whereas SquashFS often
   uses [32-byte inodes with only 4-byte timestamps](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/fs/squashfs/squashfs_fs.h?h=v6.12#n334)
   for regular files;  Consider switching to 32-byte EROFS compact inodes (e.g.,
   by using `-T`) if per-file timestamps are not a strong requirement;

 - **Lack of metadata compression**: If your testsets contain a large number of
   files, EROFS may result in larger images compared to SquashFS because of
   metadata compression is not supported.  Again, it isn't considered at first
   due to bad impacts to random metadata performance but it may be implemented
   in the future.

 - **File-based deduplication**: SquashFS deduplicates files with identical data
   by default (it can be disabled with `-no-duplicates`), whereas EROFS does not
   (except for hardlinks).  However, EROFS offers finer-grained data
   deduplication using `-Ededupe`.

 - **BCJ filters**: SquashFS can compress with XZ algorithm of BCJ enabled to
   optimize executable code.  This feature is not supported by EROFS for now,
   but there are plans to introduce BCJ filters for all EROFS-supported
   algorithms.

Note that EROFS is still under active development. The features mentioned above
are not top priorities at the moment due to limited development resources
(anyway, SquashFS has been existed for over 20 years) and target use scenarios,
but they will be considered in the future, and contributions are always welcome.
Also, note that SquashFS doesn't always outperform EROFS in image size either.
EROFS images are often significantly smaller (while still offering better
runtime performance) when compressing files in small compressed extent sizes
(especially smaller than 32KiB).

Additionally, EROFS has supported CDC-like [compressed data deduplication](design.md#data-deduplication)
since Linux 6.1, which gives extra space saving too.  Please make sure that
the options `-Ededupe` and `-Eall-fragments` are specified with `mkfs.erofs`.

## 🚧 Under construction..
