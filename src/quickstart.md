# 🚀 Get Started

## Install erofs-utils

Generally, erofs-utils can be installed directly on newer popular distributions,
although it might not be the latest stable version.

Here are examples for `Arch Linux`, `Debian`, `Fedora`, `OpenAnolis` and
`Ubuntu`:

```sh
# Arch Linux
$ sudo pacman -S erofs-utils

# Debian and Ubuntu
$ sudo apt install -y erofs-utils

# Fedora and OpenAnolis
$ sudo dnf install -y erofs-utils
```

## Build from source

### Install build dependencies

To build erofs-utils, the following dependencies will be needed:

```sh
# Debian and Ubuntu
$ sudo apt install -y autoconf automake libfuse-dev liblz4-dev liblzma-dev libtool pkg-config uuid-dev zlib1g-dev

# Fedora and OpenAnolis
$ sudo dnf install -y autoconf automake fuse-devel lz4-devel xz-devel libtool pkg-config libuuid-devel zlib-devel
```

### Download the erofs-utils source code

Use [Git](https://git-scm.com) to clone the
[erofs-utils repository](https://git.kernel.org/pub/scm/linux/kernel/git/xiang/erofs-utils.git):

```sh
$ git clone git://git.kernel.org/pub/scm/linux/kernel/git/xiang/erofs-utils.git
```

The repo defaults to the master development branch. You can also check out a release tag to build:

```sh
$ git checkout <tag> # v1.7.1, v1.6, etc.
```

### Configure and build

Please run `./autogen.sh; ./configure` from the repository's root directory.
`./configure` will prompt you for the usability of erofs-utils dependencies and
asks for additional build configuration options:

```sh
$ ./autogen.sh
$ ./configure --enable-lz4 --enable-lzma --enable-fuse
$ make
```

### Install erofs-utils

Use `make install` to install the generated files of erofs-utils:

```sh
$ sudo make install
```

## Mount

To mount an EROFS, just use the **mount** command on a block device as below:

```sh
$ mkdir ~/mnt
$ sudo mount /dev/sdX ~/mnt
```
Now all the files that are included in /dev/sdX are available
under the ~/mnt mount point.

If such EROFS image is a file, `-o loop` option can be specified together:

```sh
$ mkdir ~/mnt
$ sudo mount ~/home.erofs ~/mnt
```

Alternatively, for unprivileged users, you could also use the **erofsfuse**
command to mount an EROFS image instead:

```sh
$ mkdir ~/mnt
$ erofsfuse ~/home.erofs ~/mnt
```

## Unmount

To unmount the filesystem, use the **umount** command for privileged users:

```sh
$ sudo umount ~/mnt
```

For unprivileged users, you could also use the **fusermount** command to
unmount an instance out of ``erofsfuse``:

```sh
$ fusermount -u ~/mnt
```
