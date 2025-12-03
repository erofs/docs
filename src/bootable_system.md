# Bootable system images

## Android system partitions

EROFS was originally developed for this use case in 2017.  Nowadays, all
mainstream Android vendors use EROFS for their system partitions, leveraging
its high-performance compression to reduce image sizes without any noticeable
impact on user experience.

Known adopters include (alphabetical, may be incomplete):

 - Coolpad
 - Honor
 - Huawei
 - Motorola
 - Samsung
 - OPPO
 - Xiaomi
 - vivo

For more details on Android system partition use cases, see:

 - [EROFS AOSP user guide](https://source.android.com/docs/core/architecture/kernel/erofs)
 - [ATC'19 EROFS](https://www.usenix.org/conference/atc19/presentation/gao)

## Fedora LiveCDs

Since Fedora 42, the EROFS filesystem has been used to compress Fedora LiveCDs
to achieve smaller images with even better runtime performance.

![Starting Fedora Workstation 43 Live ISO on x86_64 (at 1.8x speed)](_static/fedora_workstation_live_43_erofs.gif)

For more details, see [Switch to EROFS for Live Media](https://fedoraproject.org/wiki/Changes/EROFSforLiveMedia).
