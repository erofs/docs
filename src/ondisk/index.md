(erofs_ondisk_format)=
# EROFS On-disk Format

EROFS uses a flexible, hierarchical, block-aligned on-disk layout that is built
with the following goals:

- DMA- and mmap-friendly, block-aligned data to maximize runtime performance on
  all kinds of storage devices;
- A simple core on-disk format that is easy to parse and has zero unnecessary
  metadata redundancy for archive use unlike other generic filesystems, ideal
  for data auditing and accessing remote untrusted data;
- Advanced on-disk features like compression (compressed inodes and metadata
  compression) are completely optional and aren’t mixed with the core design:
  you can use them only when needed.

The entire filesystem tree is built from just three core on-disk structures:

- **Superblock** — located at a fixed offset of 1024 bytes; the only
  structure at a fixed position in the filesystem.
- **Compact/Extended inodes** — per regular file, device, symlink, or directory;
  addressed in O(1) time via a simple NID-to-offset formula.
- **Directory entries** — 12-byte records, sorted lexicographically by filename
  at the beginning of each directory block (each data block of a directory inode).

Optional features extend this foundation without breaking the core design:

- **{doc}`Extended attributes (xattrs) <xattrs>`** support per-inode metadata.
  Several mechanisms — including a shared xattr pool, long prefix tables, and a
  per-inode Bloom filter — keep storage overhead low even when xattrs are used
  extensively.

```{toctree}
:hidden:
core_ondisk
xattrs
```
