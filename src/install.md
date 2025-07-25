# 📥 Installation

## Install erofs-utils via Package Managers

erofs-utils is available on most popular Linux distributions, although it may
not be the latest stable version.

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

On macOS, erofs-utils can be installed using `MacPorts` or `Homebrew`:

```sh
# MacPorts
$ sudo port install erofs-utils

# Homebrew
$ brew install erofs-utils
```

## Build from source

### Install build dependencies

To build erofs-utils, the following dependencies will be needed:

```sh
# Debian and Ubuntu
$ sudo apt install -y autoconf automake libfuse-dev liblz4-dev liblzma-dev libtool libzstd-dev pkg-config uuid-dev zlib1g-dev

# Fedora and OpenAnolis
$ sudo dnf install -y autoconf automake fuse-devel libtool libuuid-devel libzstd-devel lz4-devel pkg-config xz-devel zlib-devel
```

### Download the erofs-utils source code

Use [Git](https://git-scm.com) to clone the
[erofs-utils repository](https://git.kernel.org/pub/scm/linux/kernel/git/xiang/erofs-utils.git):

```sh
$ git clone git://git.kernel.org/pub/scm/linux/kernel/git/xiang/erofs-utils.git
```

The repo defaults to the master development branch. You can also check out a release tag to build:

```sh
$ git checkout <tag> # v1.8.10, v1.7.1, v1.6, etc.
```

### Configure and build

Please run `./autogen.sh; ./configure` from the repository's root directory.
`./configure` will prompt you for the usability of erofs-utils dependencies and
asks for additional build configuration options:

```sh
$ ./autogen.sh
$ ./configure --enable-lz4 --enable-lzma --enable-fuse --with-libzstd
$ make
```

### Install erofs-utils

Use `make install` to install the generated files of erofs-utils:

```sh
$ sudo make install
```
