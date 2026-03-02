(erofs_ondisk_format)=
# EROFS On-Disk Format

EROFS uses a compact, block-aligned on-disk layout that is deliberately kept as
minimal as possible to maximise runtime performance and simplify implementation.
The entire filesystem tree is built from just three core on-disk structures:

- **Superblock** — located at a fixed offset of 1024 bytes; the sole
  structure at a fixed position in the image.
- **Compact/Extended inodes** — one record per file, device,
  symlink, or directory; addressed in O(1) time via a simple NID-to-offset formula.
- **Directory entries** — 12-byte records, sorted lexicographically
  within each directory block.

```{toctree}
:hidden:
core_ondisk
```
