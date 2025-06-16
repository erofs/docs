# ⚖️ Features and Comparison

```{toctree}
:hidden:
comparison/dedupe.md
```

Note that it's just **an incomplete list** for the qualitative evaluation.
The overall purpose of this is to show EROFS benefits compared to other
in-kernel approaches when making technical decisions.

| Feature  (as of Linux 6.16)     | EROFS             | EXT4      | SquashFS      |
| ------------------------------- | ----------------- | --------- | ------------- |
| Minimal block size              | 512 B [^1]        | 1 KiB     | Unaligned[^2] |
| Inode size                      | 32/64 B           | 128/256 B | Varied [^3]   |
| Limitation of total UIDs/GIDs   | No                | No        | Yes (64k)[^4] |
| Pre-1970 / ns timestamps        | Yes               | Yes       | No            |
| Filesystem UUID                 | Yes               | Yes       | No            |
| Filesystem label (Volume label) | Yes               | Yes       | No            |
| Inline data                     | Yes (Inline tail) | Yes       | No            |
| Data compression                | Yes [^5]          | No        | Yes           |
| Largest compression granularity | 1 MiB             | N/A       | 1 MiB         |
| Default compression granularity | 1 Block [^6]      | N/A       | 128 KiB       |
| Fragments                       | Yes               | N/A       | Yes           |
| File-backed mounts              | Yes [^7]          | No        | No            |
| Metadata compression            | No [^8]           | N/A       | Yes           |
| Multiple compression algorithms | Per-file          | N/A       | No            |
| Data deduplication              | Extent-based      | No? [^9]  | File-based    |
| Extended attribute support      | Yes               | Yes       | Yes           |
| External data (multi-devices)   | Yes               | No        | No            |
| POSIX.1e ACL support            | Yes               | Yes       | No            |
| Direct I/O support [^10]        | Yes               | Yes       | No            |
| FIEMAP support                  | Yes               | Yes       | No            |
| SEEK_{DATA,HOLE} support        | Yes               | Yes       | No            |
| FSDAX support                   | Yes               | Yes       | No            |
| Large folio support             | Yes [^11]         | Yes [^12] | No            |
| Hardware acceleration support   | Yes [^13]         | No        | No            |

[^1]: 512-byte blocks can be used for tarball data reference.

[^2]: It means a fixed minimal filesystem I/O size which SquashFS doesn't have.
Instead, SquashFS has its own "block size": its compressed files are split up in
fixed-size blocks. See [Squashfs Binary Format/About](https://dr-emann.github.io/squashfs/squashfs.html#_about).

[^3]: SquashFS has different on-disk inodes for each type of varying contents
and size. See [Squashfs Binary Format/Inode Table](https://dr-emann.github.io/squashfs/squashfs.html#_inode_table).

[^4]: SquashFS allows 32-bit UIDs/GIDs, but only among 2{sup}`16` unique values.
See [Squashfs Binary Format/Inode Table](https://dr-emann.github.io/squashfs/squashfs.html#_inode_table).

[^5]: Data compression is an optional feature of the EROFS filesystem.
Currently, the supported compression algorithms include [LZ4](https://lz4.org),
[MicroLZMA](https://tukaani.org/xz) (since Linux 5.16),
[DEFLATE](https://datatracker.ietf.org/doc/html/rfc1951) (since Linux 6.6 LTS)
and [Zstandard](https://datatracker.ietf.org/doc/html/rfc8878) (since Linux
6.10).

[^6]: The default block size of EROFS is 4 KiB on x86 and x86-64.

[^7]: EROFS has supported [EROFS over fscache](https://lwn.net/Articles/896140)
(since Linux 5.19, deprecated in Linux 6.12) and [file-backed mounts](https://lwn.net/Articles/990750)
(since Linux 6.12) to avoid unnecessary loop devices.

[^8]: EROFS metadata is designed to be directly accessible without decoding or
deserialization (e.g., [protobuf](https://protobuf.dev/)) since they could cause
I/O amplification and extra runtime overhead in resource-limited scenarios.

[^9]: Strictly speaking, EXT4 has a feature named "[shared_blocks](https://lore.kernel.org/r/20201005161941.GF4225@quack2.suse.cz)",
which will prevents applications from writing to the filesystem.

[^10]: For example, `direct I/O` can be used for loop devices backed by
unencoded files on the EROFS filesystem to avoid double caching. `Direct I/O`
on encoded files is almost useless since it should not do ANY caching and thus
will kill the overall performance.

[^11]: EROFS has supported large folios [for uncompressed files](https://lwn.net/Articles/931794)
(since Linux 6.2) and [compressed files](https://git.kernel.org/torvalds/c/e080a26725fb) (since Linux 6.11).

[^12]: EXT4 supports [large folios since Linux 6.16](https://git.kernel.org/torvalds/c/d87d73895fcd).

[^13]: EROFS has supported [Intel QuickAssist Technology to accelerate DEFLATE
algorithm since Linux 6.16](https://git.kernel.org/torvalds/c/79b98edf918e).
