(chunk_based_inode_layout)=
# Chunk-based Inode Layout

The chunk-based inode layout splits inode data into fixed-size chunks, each mapped
to a contiguous range of physical filesystem blocks. This format supports data
deduplication and multi-device storage, allowing efficient data sharing among
different inodes and images.

## Superblock Extension for Chunk-based Inodes and Multiple Devices

The core superblock format is defined in {ref}`on_disk_superblock`. This
section lists the extended fields dedicated to chunk-based inode support and
multi-device addressing features.

| Offset | Size | Type  | Name               | Description |
|--------|------|-------|--------------------|-------------|
| 0x50   | 4    | `u32` | `feature_incompat` | `EROFS_FEATURE_INCOMPAT_CHUNKED_FILE` enables chunk-based inodes. `EROFS_FEATURE_INCOMPAT_DEVICE_TABLE` enables the device table described in {ref}`device_table` |
| 0x56   | 2    | `u16` | `extra_devices`    | Number of extra devices in addition to the primary one. Valid when `EROFS_FEATURE_INCOMPAT_DEVICE_TABLE` is set |
| 0x58   | 2    | `u16` | `devt_slotoff`     | Starting slot number of the device table on the primary device. The byte offset is `devt_slotoff * 128`. Valid when `EROFS_FEATURE_INCOMPAT_DEVICE_TABLE` is set |

## Inode Fields for Chunked Inodes

The full compact and extended inode layouts are defined in {ref}`on_disk_inodes`.
For chunk-based inodes, both inode variants share the same feature-specific
fields:

| Offset | Size | Type  | Name       | Description |
|--------|------|-------|------------|-------------|
| 0x00   | 2    | `u16` | `i_format` | Inode format hints; `EROFS_INODE_CHUNK_BASED` (4) is used for chunked inode mode |
| 0x10   | 4    | `u32` | `i_u`      | Chunk info summary described below |

## Inode Data Layout for Chunked Inodes

The following new data layout of an inode is encoded in bits 1–3 of `i_format`.

### `EROFS_INODE_CHUNK_BASED` (4)

The entire inode data is split into fixed-size chunks, each occupying consecutive
physical blocks. Requires `EROFS_FEATURE_INCOMPAT_CHUNKED_FILE`. `i_u` encodes a
chunk info summary and an array of per-chunk address entries follows the inode body.

(chunk_based_structures)=
## Chunk-based Structures

When the data layout is `EROFS_INODE_CHUNK_BASED`, the `i_u` field (4 bytes at
inode offset 0x10) is interpreted as a chunk info summary:

### Chunk Info Summary

| Bits  | Width | Description |
|-------|-------|-------------|
| 0–4   | 5     | `chunkbits`: chunk size = 2 to the power of (`blkszbits + chunkbits`) |
| 5     | 1     | `EROFS_CHUNK_FORMAT_INDEXES`: entry format selector (see below) |
| 6     | 1     | 48-bit layout specific; ignored for basic chunk-based inodes |
| 7–31  | 25    | Reserved; must be 0 |

Per-chunk extent entries are stored immediately after the core on-disk inode and
the inode xattr region. The number of entries is `⌈i_size / chunk_size⌉`.

### Chunk Entry Formats

The `EROFS_CHUNK_FORMAT_INDEXES` bit in the chunk info summary selects one of two
per-chunk entry formats:

(chunk-entry-formats-block-map-entry)=
#### Block Map Entry (4 bytes)

When `EROFS_CHUNK_FORMAT_INDEXES` is not set, each chunk is described by a
single 32-bit block address entry.

Without a device table, this entry is a primary-device block address.
With `EROFS_FEATURE_INCOMPAT_DEVICE_TABLE`, it is interpreted in
the unified address space and can resolve to either the primary or an extra device.

| Offset | Size | Type  | Name       | Description |
|--------|------|-------|------------|-------------|
| 0x00   | 4    | `u32` | `startblk` | Starting block address of this chunk |

#### Chunk Index Entry (8 bytes)

When `EROFS_CHUNK_FORMAT_INDEXES` is set, each chunk is described by an 8-byte
record that supports multi-device addressing.

| Offset | Size | Type  | Name        | Description |
|--------|------|-------|-------------|-------------|
| 0x00   | 2    | `u16` | _dontcare_  | 48-bit layout specific; ignored for basic chunk-based inodes |
| 0x02   | 2    | `u16` | `device_id` | Device selector. `0` uses unified-address-space resolution; non-zero values directly select extra devices |
| 0x04   | 4    | `u32` | `startblk`  | 32-bit starting block address; interpretation depends on `device_id` |

When `device_id` is `0`, `startblk` is interpreted exactly like a
{ref}`Block Map Entry (4 bytes) <chunk-entry-formats-block-map-entry>`:
it is an absolute block address in the unified address space. When
`device_id` is non-zero, it directly selects an extra device and `startblk`
is interpreted as a block address on that device. See
{ref}`block-address-resolution-for-chunk-based-inodes`.

(multi_device_support)=
## Multi-device Support

(device_table)=
### Device Table

This section applies when `EROFS_FEATURE_INCOMPAT_DEVICE_TABLE` is set.

When `EROFS_FEATURE_INCOMPAT_DEVICE_TABLE` is set, the `extra_devices` superblock
field gives the number of additional block devices. They are described by an array
of 128-byte device slot records stored on the primary device. The first record
begins at byte offset `devt_slotoff * 128`.

Each record contains:

| Offset | Size | Type   | Name       | Description |
|--------|------|--------|------------|-------------|
| 0x00   | 64   | `u8[]` | `tag`      | User-specific identifier: The kernel never parses it in any form |
| 0x40   | 4    | `u32`  | `blocks`   | 32-bit total block count of this device |
| 0x44   | 4    | `u32`  | `uniaddr`  | 32-bit unified starting block address of this device |
| 0x48   | 4    | `u8[]` | _dontcare_ | 48-bit layout specific; ignored for basic chunk-based inodes |
| 0x4C   | 52   | `u8[]` | _reserved_ | Reserved; must be 0 |

(block-address-resolution-for-chunk-based-inodes)=
### Block Address Resolution for Chunk-based Inodes

#### Chunk Index Entry

When the chunk index entry format is used, `device_id` controls how
`startblk` is interpreted:

- `device_id = 0`: `startblk` is an absolute block address in the unified
  address space; see {ref}`Block Map Entry <block-map-entry-address-resolution>`
  for details.
- `device_id = N` (1 ≤ N ≤ `extra_devices`): `startblk` is a block address on
  extra device N, whose record begins at byte offset
  `(devt_slotoff + N - 1) * 128` on the primary device.

(block-map-entry-address-resolution)=
#### Block Map Entry

The simple block map entry format has no `device_id` field. Instead, `startblk`
is an absolute block address in the unified address space, and the reader uses
`uniaddr` from the device table to identify the target device: it finds the
slot `i` whose range `[uniaddr[i], uniaddr[i] + blocks[i])` contains
`startblk`, then derives the intra-device block address as
`startblk − uniaddr[i]`. Chunk index entries with `device_id = 0` use this
same interpretation.
