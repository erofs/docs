# Deduplication among versions

## Minor container image updates

- Examine 10 versions of ubuntu:jammy from [Docker Hub](https://hub.docker.com/_/ubuntu), specifically
jammy-{20221130,20230126,20230301,20230308,20230425,20230522,20230605,20230624,20230804,20230816};

- These images only have one layer which is in the tar.gz format;

- Uncompressed EROFS images are built with `-Ededupe` and compressed EROFS images are built with
`-Ededupe,all-fragments` and LZ4HC, DEFLATE algorithms.

|                                   | Total Size (MiB) | Average layer size (MiB) | Saved / 766.1MiB |
| --------------------------------- | ---------------- | ------------------------ | ---------------- |
| Compressed OCI (tar.gz)           | 282.5            | 28.3                     | 63%              |
| Uncompressed OCI (tar)            | 766.1            | 76.6                     | 0%               |
| Uncompressed EROFS                | 109.5            | 11.0                     | 86%              |
| EROFS (DEFLATE,9,32k)             | 46.4             | 4.6                      | 94%              |
| EROFS (LZ4HC,12,64k)              | 54.2             | 5.4                      | 93%              |
| SquashFS (GZIP,9,128k,-noI [^1])  | 47.0             | 4.7                      | 94%              |
| SquashFS (LZ4HC,12,128k,-noI)     | 54.7             | 5.5                      | 93%              |

[^1]: SquashFS uses `–b 131072` by default, `-noI` will disable its metadata
compression.

It shows that EROFS gets **smaller sizes** even with smaller compression
granularity.

## [Wikipedia](https://en.wikipedia.org) snapshots

Two [snapshots](https://dumps.wikimedia.org/enwiki) were selected: `20230201`
and `20230220`:

 - Each snapshot included the first 100 pages at that time.

 - There was 20-day difference between each other.

|                            | Deduped? | Size (MiB) | Saved / 1888MiB |
| -------------------------- | -------- | ---------- | --------------- |
| Uncompressed text          | No       | 1888       | 0%              |
| SquashFS [4k] [^2]         | No       | 1235       | 34.6%           |
| EROFS [4k, _default_]      | No       | 1201       | 36.4%           |
| SquashFS [8k]              | No       | 1150       | 39.1%           |
| EROFS [4k] [^3]            | Yes      | 1147       | 39.2%           |
| SquashFS [128k, _default_] | No       | 1110       | 41.2%           |
| EROFS [64k]                | Yes      | 988        | 47.7%           |

[^2]: SquashFS command line: `-comp lz4 -b # -noappend`
[^3]: EROFS command line: `-zlz4 -Ededupe -C #`

## [Linux kernel source code](https://www.kernel.org) releases

[Three kernel releases](https://www.kernel.org/pub/linux/kernel/v5.x) are
selected: `5.10`, `5.10.50`, `5.10.100`:

 - Images from both filesystems are compressed with `LZ4HC, 12` since SquashFS
   uses the maximum level 12 for LZ4HC;

 - EROFS images are built with `-T0 --force-uid=1000 --force-gid=100` in
   order to force 32-byte inodes to approximately match SquashFS metadata size;

|                            | Fragments? | Deduped? | Size    |
| -------------------------- | ---------- | -------- | ------- |
| SquashFS [16k]             | Yes        | No       | 409 MiB |
| EROFS [4k, _default_]      | Yes        | Yes      | 379 MiB |
| SquashFS [32k]             | Yes        | No       | 365 MiB |
| EROFS [8k]                 | Yes        | Yes      | 347 MiB |
| SquashFS [64k]             | Yes        | No       | 334 MiB |
| EROFS [32k]                | Yes        | Yes      | 313 MiB |
| SquashFS [128k, _default_] | Yes        | No       | 312 MiB |
| EROFS [64k]                | Yes        | Yes      | 310 MiB |
