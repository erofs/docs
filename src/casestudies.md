# 🔍 Case Studies

```{toctree}
:hidden:
bootable_system.md
```

The EROFS filesystem has been deployed in production at large scale since its
inclusion in Linux 5.4 and is now part of several prominent open-source
ecosystems.

It started in 2017, when Linux image filesystems were still primitive
([cramfs](https://docs.kernel.org/filesystems/cramfs.html) and
[ROMFS](https://docs.kernel.org/filesystems/romfs.html)), or
focused solely on extreme image size reduction
([squashfs](https://docs.kernel.org/filesystems/squashfs.html)) for low-end
embedded devices, while lacking good real-time response in
[low memory scenarios](https://web.archive.org/web/20220322054637/https://source.android.com/devices/architecture/kernel/squashfs#:~:text=Unfortunately%20the%20performance%20of%20SquashFS%20lags%20behind%20ext4.).
In addition, kernel development for most in-tree immutable filesystems
(particularly on-disk format enhancements) was inactive for a decade at that
time.

To meet our production performance needs and fill the gap for a better
high-performance Linux image filesystem, the EROFS project was launched. Before
being successfully upstreamed, it had already been successfully deployed on
millions of Android smartphones and it should be billions of various devices
now.

Note that the EROFS filesystem aims to be a generic image filesystem from the
beginning, not limited to a specific use case (e.g. only for Android system
partitions). We believe that even if image filesystems have certain useful use
cases, in reality it often fails to attract many real experienced kernel
filesystem developers. Designing a specialized filesystem for a single use case
will lead to unhealthy development, unnecessary reinvention, and fragmentation.

Currently, apart from the [initial Android use cases](https://source.android.com/docs/core/architecture/kernel/erofs),
we are also focused on bringing up a better image filesystem for containers.
Many recent features, such as native layering support, large folios,
[file-backed mounts](https://lwn.net/Articles/990750/),
[inode-based page cache sharing](https://lwn.net/Articles/984839/), and
[direct access for files](https://docs.kernel.org/filesystems/dax.html), are
dedicated to container image use cases.

In several popular projects, EROFS is used as a powerful tool to provide
advanced features or improve the de-facto standard Docker/OCI container images,
such as [ComposeFS](https://github.com/containers/composefs) and
the [EROFS containerd snapshotter](https://github.com/containerd/containerd/pull/10705).
However, EROFS can also serve as a next-generation container filesystem on its
own. We believe it should be more useful as the EROFS container ecosystem
continues to evolve.

The EROFS filesystem is now a completely community-driven, neutral open-source
project and part of the Linux kernel. If you’re working on, or interested in
image filesystem use cases, feel free to provide feedback and join us.

🚧 Detailed introduction to the current main use cases is still in progress.
