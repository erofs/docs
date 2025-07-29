# 📦 Build & Mount

## Creating an EROFS filesystem

To create an EROFS image, use the **mkfs.erofs(1)** utility provided by
erofs-utils.

### From a local directory

You can create an EROFS image directly from a local directory:
```sh
$ mkfs.erofs [OPTIONS] <IMAGE> <SOURCE DIRECTORY>
```

By default, `mkfs.erofs` creates plain images, as compression is an optional
on-disk feature.  Compression and other behaviors can be configured via
command-line options.

Here are some frequently used options for mkfs.erofs:

| Option             | Description                                                                                                  |
| ------------------ | ------------------------------------------------------------------------------------------------------------ |
| -z X[,level=#]     | Specify a valid compressor [^1] and, optionally, a compression level.                                        |
| -C #               | Specify the physical cluster size for compression (default: filesystem block size).                          |
| -b #               | Specify the filesystem block size (default: system page size, e.g. 4096).                                    |
| -T #               | Set the UNIX timestamp for the filesystem. It will behave as `--all-time` if `--mkfs-time` is not specified. |
| --all-time         | (used together with `-T`) Set all files to the fixed timestamp.                                              |
| --mkfs-time        | (used together with `-T`) The given timestamp is only applied to the image creation time.                    |
| -U X               | Specify the filesystem UUID, or one of the following value: clear, random.                                   |
| -E ztailpacking    | Inline the tail parts of compressed files into their metadata.                                               |
| -E fragments       | Pack the tail parts of compressed files, or entire files if they are small, into a special inode.            |
| -E all-fragments   | (not recommended) Pack entire files into a special inode to reduce image size.                               |
| -E dedupe          | Enable global data deduplication [^2]. Note: not supported with multi-threading *yet*.                       |

For example, to generate an uncompressed EROFS image from `foo/`:

``` sh
$ mkfs.erofs foo.erofs foo/
```

To generate a compressed EROFS image using LZ4HC (level 12), with `fragments`
and `ztailpacking` features enabled, and the physical cluster size of 65536:
``` sh
$ mkfs.erofs -zlz4hc,12 -C65536 -Efragments,ztailpacking foo.erofs foo/
```

:::{note}

By default, EROFS just uses a physical cluster size equal to the block size
(e.g., 4096 on x86) and disables advanced features to keep the random access
performance. Consider increasing `-C` and enabling advanced features if
a smaller image size is desired.

Using `-Eall-fragments` is not recommended now, as it can degrade runtime
performance unless minimizing image size is the top priority. `-Efragments`
already supports multi-threading.

:::

[^1]: Supported compressors: lz4, lz4hc, lzma, deflate, libdeflate, and zstd.
[^2]: If data compression (encoded data) is enabled, rolling-hash-based
      deduplication will be used; otherwise, block-based deduplication will be
      applied.

### From a tarball file

Alternatively, an EROFS image can also be generated from a tarball file
using the `--tar` command-line option.

Here are some frequently used additional options for `mkfs.erofs` tar mode:

| Option      | Description                                                                                  |
| ----------- | -------------------------------------------------------------------------------------------- |
| --tar=f     | Generate a full EROFS image from a regular tarball.                                          |
| --tar=i     | Generate a meta-only EROFS image from a regular tarball.                                     |
| --aufs      | Convert AUFS special files to OverlayFS metadata (commonly used in Docker/OCI images).       |
| --sort=none | (only valid with `--tar=f`) Keep inode data order consistent with tar data order.            |
| --sort=path | (only valid with `--tar=f`) Data order strictly follows the tree generation order (default). |

For example, to generate an full EROFS image from a tarball `foo.tar`:

```sh
$ mkfs.erofs --tar=f --sort=none foo.erofs foo.tar
```

Note that `--sort=none` is used if strict data order is not required; it helps
eliminate unnecessary data writes.

Additionally, `--tar=i` can be used to generate a minimized EROFS metadata index
that references external tar data:

```sh
$ mkfs.erofs --tar=i foo.erofs foo.tar
```

The generated tar index EROFS image can be used with the original tar file
specified using the mount option `-odevice=`. Alternatively, you can append
the original tar file to the tar index:
```sh
cat foo.tar >> foo.erofs
```

## Mount

To mount an EROFS image, use the **mount(8)** command on a block device or
a regular EROFS image file, as shown below:

```sh
$ mkdir ~/mnt
$ sudo mount /dev/sdX ~/mnt
```

All files contained in `/dev/sdX` will now be accessible under the `~/mnt`
mount point.

If the image is a regular file and the command above doesn't work (e.g., due
to an older version of util-linux), you can use the `-o loop` option:

```sh
$ mkdir ~/mnt
$ sudo mount -o loop foo.erofs ~/mnt
```

Alternatively, unprivileged users can mount an EROFS image using **erofsfuse**:

```sh
$ mkdir ~/mnt
$ erofsfuse foo.erofs ~/mnt
```

## Unmount

To unmount the filesystem, use the **umount (8)** command for privileged users:

```sh
$ sudo umount ~/mnt
```

For unprivileged users, you could also use the **fusermount** command to
unmount an instance out of ``erofsfuse``:

```sh
$ fusermount -u ~/mnt
```
