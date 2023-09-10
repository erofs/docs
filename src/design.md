# 📝 Technical Design

The following sections are summarized technical description for reference if
you are a user or developer interested in getting more EROFS internals. By the
way, a paper is also available for everyone to look into [EROFS: A Compression-friendly
Readonly File System for Resource-scarce Devices](https://www.usenix.org/conference/atc19/presentation/gao).
The detailed format in this paper is slightly outdated but overall ideas are
almost the same.

## Block-aligned vs unaligned

EROFS data is all arranged in **fixed-size blocks** (aka. block-aligned,
typically 4 KiB) as many modern disk filesystems (e.g. ext4, xfs, btrfs, f2fs,
etc.) to match intrinsic characteristics of [block devices](https://en.wikipedia.org/wiki/Block_\(data_storage\)).
It means the corresponding data can be *directly* parsed if you read a single
filesystem block for __non-encoded data__ or (maybe) multiple consecutive blocks
(called a single physical cluster) for __encoded data__, which is different
from _archive formats or unaligned filesystems_ (e.g. cramfs, romfs, squashfs,
affs, or maybe more FUSE-based implementations.)

![Comparsion between unaligned and block-aligned data](_static/aligned_io.svg)

The main benefits of using fixed-size blocks are:

 - Block-aligned non-encoded EROFS data can be directly loaded into kernel page
   cache and memory-mapped into userspace **without any extra post-processing**.
   Direct I/O and FSDAX can also be used for block-aligned non-encoded EROFS
   data.

 - Block-aligned encoded EROFS data I/Os can be **fully utilized**, which means
   there is no unusable encoded byte in each single I/O request.  Unlike other
   unaligned approaches, unstrictly speaking, EROFS doesn't have to cache such
   unusable encoded bytes for later decoding (or never used) for better
   performance (otherwise I/O efficiency for small random I/Os is low due to
   undecodable encoded bytes), which is considered as harmful due to larger
   memory footprints than necessary.

 - Alternatively, if the full encoded blocks doesn't really needed to be
   utilized immediately (esp. very little decoded data is requested), such
   encoded blocks could be _still cached in the page cache for later use_.
   It's quite useful on memory-limited devices since _caching compressed data
   is generally more efficient than decompressed data if selected compression
   algorithms is **fast** enough_ (considering main benefits of ZSWAP or ZRAM).
   Although unaligned solutions could also cache encoded data in page cache,
   reclaiming could lead to the remaining cached pages harder to be utilized
   even further due to fragmentation since page cache reclaims data in pages
   instead of bytes.

 - Because of this, block-aligned encoded EROFS makes **compresssed data cached
   independently**, which means a single physical cluster could be cached
   without coupling with other compression units.  In other words, unlike
   unaligned solutions, It's more flexible for EROFS to only cache needed
   physical clusters.

![Different compressed cache behaviors](_static/unaligned_reclaiming.svg)

(compression_dedupe)=

## Block-aligned fitblk compression

In addition to block-aligned data, unlike ext4, xfs, btrfs, f2fs, etc., EROFS
mainly uses a called **fixed-size output compression** approach to extremely
utilize encoded blocks and maximize compression ratios.

Such compression approach is not a MUST but the final blocks of physical
clusters could not be fully filled with encoded data otherwise.  Currently LZ4,
LZMA and DEFLATE algorithms natively support this mode.

Fixed-size output compression generally has better compression ratios especially
on small physical clusters (e.g. 4 or 8 KiB) with about 5% extra space saving.

Note that **small compressed physical clusters** are quite important to
end-to-end performance for memory-intensive workloads (that is exactly the EROFS
main target case) since it's quite hard to fully cache either (de)compressed
data in memory on such extreme workloads.  In other words, reloading can happen
frequently due to cache misses on these workloads.

## Data deduplication

EROFS supports both _fixed-size chunk deduplication_ and _compressed data
deduplication_:

 - For non-encoded files, data can be splitted into fixed-size chunks for
   mmap-I/O friendly and only keep chunks with different contents on disk.

 - For encoded files, each physical cluster can be used in a similar way for
   multiple reference.  Note that cut points will be adjusted with Rabin–Karp
   rolling-hashing approach to find more possibilities.

![EROFS deduplication](_static/erofs_dedupe.svg)

## In short: why is EROFS designed for performance?

Here is a summary of our overall design as below:

 - Block-aligned data - No extra I/O waste;

 - Fixed-size output compression - better compression ratios as well as
   efficient I/O utilization;

 - Independent cached or inplace I/O strategies - to minimize memory footprints;

 - Inplace decompression - to avoid bounced compressed buffers and poisoned
   cachelines as much as possible;

 - Multi-reference compressed clusters - to avoid deduplicated data I/O (not
   always) and minimize images even further.

```{toctree}
:hidden:
core_ondisk.md
merging.md
```
