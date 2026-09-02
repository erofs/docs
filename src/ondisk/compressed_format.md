(compressed_inode_layout)=
# Compressed Format Layout

## Inode Data Layouts for Compression

EROFS supports per-file data compression using two inode data layouts:
`EROFS_INODE_COMPRESSED_FULL` and `EROFS_INODE_COMPRESSED_COMPACT`.

### `EROFS_INODE_COMPRESSED_FULL` (1)

The inode data region begins with a compression map header, followed by the logical
cluster index. See {ref}`compression_map_header` for the full format.

### `EROFS_INODE_COMPRESSED_COMPACT` (3)

A compact variant of the compressed layout. The map header and cluster index use
a narrower encoding to reduce metadata overhead for small files. See
{ref}`compacted-logical-cluster-index` for the full format.

## Superblock Fields for Compression

The core superblock format is defined in {ref}`on_disk_superblock`. This
section lists the extended fields dedicated to compression features.

| Offset | Size | Type  | Name               | Description |
|--------|------|-------|--------------------|-------------|
| 0x50   | 4    | `u32` | `feature_incompat` | Incompatible feature flags; see {ref}`compression-feature-flags` |
| 0x54   | 2    | `u16` | `is_compressed`    | Compression marker and configuration field. See {ref}`compression-algorithm-field` for the compression-specific interpretation |
| 0x60   | 8    | `u64` | `packed_nid`       | Packed inode NID. Relevant when fragment data is stored in the packed inode's data region; see {ref}`packed-inode` |
| 0x80   | 8    | `u64` | `metabox_nid`      | Metabox inode NID. Relevant when compressed metadata is stored in the metabox inode's data region; valid when `sb_extslots >= 1`; see {ref}`metabox-inode` |

(compression-feature-flags)=
### Compression Feature Flags

The following `feature_incompat` bits are relevant to compression:

| Bit mask     | Name                                    | Description |
|--------------|-----------------------------------------|-------------|
| `0x00000001` | `EROFS_FEATURE_INCOMPAT_LZ4_0PADDING`   | Trailing zero-padding in compressed clusters |
| `0x00000002` | `EROFS_FEATURE_INCOMPAT_COMPR_CFGS` / `EROFS_FEATURE_INCOMPAT_BIG_PCLUSTER` | Compression configuration is present; see {ref}`compr_cfgs_records`. The same bit is also the compatibility flag for big pclusters, which allow a single pcluster to span more than one block |
| `0x00000008` | `EROFS_FEATURE_INCOMPAT_COMPR_HEAD2`    | Head2 cluster type may be used for a second compression algorithm |
| `0x00000010` | `EROFS_FEATURE_INCOMPAT_ZTAILPACKING`   | Compressed tail data inlined into metadata block |
| `0x00000020` | `EROFS_FEATURE_INCOMPAT_FRAGMENTS`      | Fragment packing via packed inode; see {ref}`packed-inode` |
| `0x00000100` | `EROFS_FEATURE_INCOMPAT_METABOX`        | Metadata may be stored in the metabox inode; see {ref}`metabox-inode` |

(compression-algorithm-field)=
### Compression Algorithm Field (Offset 0x54)

The core format treats superblock offset 0x54 as `is_compressed`: any non-zero
value marks a compressed image, but `0` does not by itself prove that the image
is plain. `EROFS_FEATURE_INCOMPAT_LZ4_0PADDING` also marks a legacy LZ4-only
compressed image. For compressed images, the same 16-bit field has two
compression-specific interpretations:

- **`available_compr_algs`**: when `EROFS_FEATURE_INCOMPAT_COMPR_CFGS` is
  **set**, this field is a bitmap indicating which compression algorithms have
  per-algorithm configuration records stored in the metadata area immediately
  after the superblock block.
- **`lz4_max_distance`**: when `EROFS_FEATURE_INCOMPAT_COMPR_CFGS` is
  **not set**, the image can only use LZ4 compression. This field stores the
  customised LZ4 sliding-window size directly in the superblock; 0 means the LZ4
  default.

Each bit in `available_compr_algs` corresponds to one algorithm:

| Bit | Mask     | Constant                       | Algorithm |
|-----|----------|--------------------------------|-----------|
| 0   | `0x0001` | `Z_EROFS_COMPRESSION_LZ4`      | LZ4       |
| 1   | `0x0002` | `Z_EROFS_COMPRESSION_LZMA`     | LZMA      |
| 2   | `0x0004` | `Z_EROFS_COMPRESSION_DEFLATE`  | Deflate   |
| 3   | `0x0008` | `Z_EROFS_COMPRESSION_ZSTD`     | Zstandard |

For the layout of the per-algorithm configuration records that follow the superblock
block, see {ref}`compr_cfgs_records`.

Compressed inodes support up to two simultaneous compression algorithms, referred
to as algorithm 1 (head1) and algorithm 2 (head2). Each logical cluster
index entry is typed as either `HEAD1`, `HEAD2`, `PLAIN`, or `NONHEAD`:
`HEAD1` marks the start of an extent compressed with algorithm 1, and `HEAD2`
marks the start of an extent compressed with algorithm 2. Using two algorithms in
one file is optional — a file may use only HEAD1 with the head2 nibble set to 0.

(packed-inode)=
### Packed Inode

The packed inode is enabled by `EROFS_FEATURE_INCOMPAT_FRAGMENTS`. Its NID is stored
in the superblock field `packed_nid`. It is a normal inode whose data region is a
linear byte stream into which fragment data from multiple files is packed contiguously.
The packed inode itself may use compressed layouts, so the fragment data it contains
may itself be compressed.

The packed inode does not appear in any directory's entry list. It is referenced
exclusively by inodes whose data is wholly or partially stored as fragments. See
{ref}`fragment-mode` for details.

(metabox-inode)=
### Metabox Inode

The metabox inode is enabled by `EROFS_FEATURE_INCOMPAT_METABOX`. Its NID is stored
in the superblock field `metabox_nid`. It is a normal inode whose data region stores
inode metadata for inodes embedded within it rather than occupying independent inode
slots in the metadata area. The metabox inode itself may use compressed layouts, so
the metadata blocks it contains may themselves be compressed. Its data region is
always accessed as a decoded byte stream.

#### Directory Entry Reference

A directory entry whose `nid` has bit 63 (`EROFS_DIRENT_NID_METABOX_BIT`) set refers
to an inode embedded in the metabox inode's decoded data region. The directory entry
has the following layout:

| Offset | Size | Type  | Name        | Description |
|--------|------|-------|-------------|-------------|
| 0x00   | 8    | `u64` | `nid`       | Node number; bit 63 = `EROFS_DIRENT_NID_METABOX_BIT` indicates metabox-embedded inode; lower 63 bits = slot index |
| 0x08   | 2    | `u16` | `nameoff`   | Byte offset of the filename within this directory block |
| 0x0A   | 1    | `u8`  | `file_type` | File type code |
| 0x0B   | 1    | `u8`  | `reserved`  | Reserved; must be 0 |

When bit 63 is set, the lower 63 bits (`nid & EROFS_DIRENT_NID_MASK`) serve as the
slot index; the inode is located at
`metabox_data_start + 32 × (nid & EROFS_DIRENT_NID_MASK)` rather than in the normal
metadata area. The metabox inode itself does not appear in any directory's entry list.

(compr_cfgs_records)=
## Per-algorithm Configuration Records

When `EROFS_FEATURE_INCOMPAT_COMPR_CFGS` is set, per-algorithm configuration
records are stored in the metadata area immediately after the superblock.
Records appear in ascending bit-position order of `available_compr_algs` (LZ4
first if present, then LZMA, etc.), one record for each set bit.
Each record begins with a 2-byte `length` field; the value of `length` counts
only the payload after that field, so the total record size is `length + 2`
bytes.

**LZ4** (16 bytes total)

| Offset | Size | Type   | Name               | Description |
|--------|------|--------|--------------------|-------------|
| 0x00   | 2    | `u16`  | `length`           | Payload size in bytes (= 14) |
| 0x02   | 2    | `u16`  | `max_distance`     | Maximum LZ4 back-reference distance in bytes |
| 0x04   | 2    | `u16`  | `max_pclusterblks` | Maximum LZ4 pcluster size in blocks across this image; 0 is a reserved case and will be treated as 1 |
| 0x06   | 10   | `u8[]` | `reserved`         | Reserved; must be 0 |

**LZMA** (16 bytes total)

| Offset | Size | Type   | Name        | Description |
|--------|------|--------|-------------|-------------|
| 0x00   | 2    | `u16`  | `length`    | Payload size in bytes (= 14) |
| 0x02   | 4    | `u32`  | `dict_size` | LZMA/MicroLZMA dictionary size in bytes; valid range 4KiB – 8 MiB; 0 = implementation-defined default |
| 0x06   | 2    | `u16`  | `format`    | Reserved; must be 0 |
| 0x08   | 8    | `u8[]` | `reserved`  | Reserved; must be 0 |

**Deflate** (8 bytes total)

| Offset | Size | Type   | Name         | Description |
|--------|------|--------|--------------|-------------|
| 0x00   | 2    | `u16`  | `length`     | Payload size in bytes (= 6) |
| 0x02   | 1    | `u8`   | `windowbits` | Base-2 logarithm of the DEFLATE decompressor window size |
| 0x03   | 5    | `u8[]` | `reserved`   | Reserved; must be 0 |

**Zstandard** (8 bytes total)

| Offset | Size | Type   | Name        | Description |
|--------|------|--------|-------------|-------------|
| 0x00   | 2    | `u16`  | `length`    | Payload size in bytes (= 6) |
| 0x02   | 1    | `u8`   | `format`    | Reserved; must be 0 |
| 0x03   | 1    | `u8`   | `windowlog` | Base-2 logarithm of the ZSTD decompressor window size, offset by 10; actual window size = `1 << (windowlog + 10)` |
| 0x04   | 4    | `u8[]` | `reserved`  | Reserved; must be 0 |

## Per-inode Compression Metadata

(compression_map_header)=
### Compression Map Header (8 bytes)

The map header is stored at the start of the inode data region for compressed
layouts. The layout and interpretation below apply to the **normal compressed
inode** case — i.e. when bit 63 of the 8-byte header (as a little-endian `u64`)
is **0** (all-fragments mode is not active) and `Z_EROFS_ADVISE_EXTENTS` is
**not** set. See {ref}`all_fragments_mode`
and {ref}`encoded_extents` for the two
alternate layouts.

| Offset | Size | Type  | Name                             | Description |
|--------|------|-------|----------------------------------|-------------|
| 0x00   | 4    | `u32` | `h_fragmentoff` / `h_idata_size` | Union; interpretation depends on flags (see below) |
| 0x04   | 2    | `u16` | `h_advise`                       | Advisory flags |
| 0x06   | 1    | `u8`  | `h_algorithmtype`                | Algorithm IDs: bits 0–3 = algorithm 1 (HEAD1 clusters), bits 4–7 = algorithm 2 (HEAD2 clusters) |
| 0x07   | 1    | `u8`  | `h_clusterbits`                  | Logical cluster size = `2^(blkszbits + bits[0:3])`; bits 4–6 reserved; bit 7 = `Z_EROFS_FRAGMENT_INODE_BIT` (must be 0 in this mode) |

#### Offset 0x00 Union Interpretation

The offset 0x00 union has two tail-storage interpretations.

When `Z_EROFS_ADVISE_FRAGMENT_PCLUSTER` is set in `h_advise`:

| Bits | Type | Field | Meaning |
|------|------|-------|---------|
| 0–31 | `u32` | `h_fragmentoff` | Byte offset of the tail fragment within the packed inode's data region |

When `Z_EROFS_ADVISE_INLINE_PCLUSTER` is set in `h_advise`:

| Bits | Type | Field | Meaning |
|------|------|-------|---------|
| 0–15 | `u16` | `h_reserved1` | Reserved; must be 0 |
| 16–31 | `u16` | `h_idata_size` | Size of inline tail data following the cluster index |

If both bits are present, `Z_EROFS_ADVISE_FRAGMENT_PCLUSTER` takes precedence.

#### `h_advise` Flags

Bit `0x0001` has two mutually exclusive meanings depending on the layout variant:
`Z_EROFS_ADVISE_COMPACTED_2B` for `EROFS_INODE_COMPRESSED_COMPACT`, and
`Z_EROFS_ADVISE_EXTENTS` for `EROFS_INODE_COMPRESSED_FULL`. When
`Z_EROFS_ADVISE_EXTENTS` is set, the remaining flags and the map header layout
differ; see {ref}`encoded_extents`.

| Bit mask | Name | Description |
|----------|------|-------------|
| `0x0001` | `Z_EROFS_ADVISE_COMPACTED_2B`        | (`EROFS_INODE_COMPRESSED_COMPACT` only) Compact 2-byte cluster index entries |
| `0x0001` | `Z_EROFS_ADVISE_EXTENTS`             | (`EROFS_INODE_COMPRESSED_FULL` only) Encoded extent array; see {ref}`encoded_extents` |
| `0x0002` | `Z_EROFS_ADVISE_BIG_PCLUSTER_1`      | Head1 clusters use big-pcluster encoding |
| `0x0004` | `Z_EROFS_ADVISE_BIG_PCLUSTER_2`      | Head2 clusters use big-pcluster encoding |
| `0x0008` | `Z_EROFS_ADVISE_INLINE_PCLUSTER`     | Inline (ztailpacking) tail data present |
| `0x0010` | `Z_EROFS_ADVISE_INTERLACED_PCLUSTER` | Interlaced pcluster layout |
| `0x0020` | `Z_EROFS_ADVISE_FRAGMENT_PCLUSTER`   | Tail fragment stored in packed inode |

### Logical Cluster Index Entry (8 bytes)

One index entry exists per logical cluster. Entries are stored contiguously
immediately after the map header.

| Offset | Size | Type  | Name            | Description |
|--------|------|-------|-----------------|-------------|
| 0x00   | 2    | `u16` | `di_advise`     | Cluster type and flags |
| 0x02   | 2    | `u16` | `di_clusterofs` | Byte offset of this logical cluster's start within the physical cluster |
| 0x04   | 4    | `u32` | `di_u`          | Physical block address (head clusters) or delta to head (non-head clusters) |

According to cluster type, `di_u` will be interpreted as:
- `di_blkaddr` (4 bytes) for `HEAD1`, `HEAD2`, and `PLAIN` clusters,
  giving the physical block address of the cluster's data.
- `di_u.delta[0]` and `di_u.delta[1]` (2 bytes each) for `NONHEAD`
  clusters, giving the distance back to the HEAD cluster and the
  lookahead distance to the next HEAD cluster, respectively.

Cluster types encoded in `di_advise` bits 0–1:

| Value | Type                          | Description |
|-------|-------------------------------|-------------|
| 0     | `Z_EROFS_LCLUSTER_TYPE_PLAIN`  | Uncompressed; maps directly to physical blocks |
| 1     | `Z_EROFS_LCLUSTER_TYPE_HEAD1`  | First entry of a compressed extent (algorithm 1) |
| 2     | `Z_EROFS_LCLUSTER_TYPE_NONHEAD`| Continuation of a preceding head cluster |
| 3     | `Z_EROFS_LCLUSTER_TYPE_HEAD2`  | First entry of a compressed extent (algorithm 2) |

Additional flag bits in `di_advise`:

| Bit mask | Name                    | Applicable lcluster type | Description |
|----------|-------------------------|--------------------------|-------------|
| `0x0800` | `Z_EROFS_LI_D0_CBLKCNT` | NONHEAD (first only) | When set, `di_u.delta[0]` carries the compressed block count of the preceding pcluster instead of a distance to the HEAD lcluster. Only meaningful when {ref}`big-physical-cluster` is active (`Z_EROFS_ADVISE_BIG_PCLUSTER_{1,2}`). |
| `0x8000` | `Z_EROFS_LI_PARTIAL_REF` | HEAD1 / HEAD2 (non-compact only) | The pcluster's decompressed output is only partially consumed: the logical data start at offset `di_clusterofs` rather than 0. |

(compacted-logical-cluster-index)=
#### Compacted Logical Cluster Index

Inode layout `EROFS_INODE_COMPRESSED_COMPACT` encodes logical cluster entries as
a packed bitstream immediately after the 8-byte map header.
Enabling this feature requires the logical cluster size to be no more than
16 KiB (`lclusterbits <= 14`).
If `Z_EROFS_ADVISE_COMPACTED_2B` is set in `h_advise`, this lcluster bit size
limit is further reduced to 12 bits (`lclusterbits <= 12`).

##### Compacted Lcluster Entry Format
Each encoded lcluster entry is a codeword, where `lobits = max(lclusterbits, 12)`:

```
v = (type << lobits) | lo
```

The fields are:

| Field  | Width    | Description |
|--------|----------|-------------|
| `type` | 2 bits   | Cluster type: `PLAIN`, `HEAD1`, `NONHEAD`, or `HEAD2` |
| `lo`   | `lobits` | Payload; interpretation depends on cluster type (see below) |

For `HEAD1`, `HEAD2`, and `PLAIN` lclusters, `lo` carries `clusterofs`.

For `NONHEAD` lclusters, `lo` interpretation depends on position and flags:

| Condition | `lo` carries | Description |
|-----------|--------------|-------------|
| Last `NONHEAD` entry in a pack | `di_u.delta[1]` | Lookahead distance to the next HEAD entry |
| Otherwise | `di_u.delta[0]` | Lookback distance back to the HEAD entry (or compressed block count of the preceding pcluster if `Z_EROFS_LI_D0_CBLKCNT` is set in `di_advise`, see {ref}`big-physical-cluster` for details) |

##### Compacted Lcluster Entry Packs Layout

Lcluster entries are grouped into fixed-size **packs**, each ending with a 32-bit
little-endian `blkaddr` used to reconstruct HEAD physical block addresses.

There are two pack modes: **4-byte pack** is always supported, while **2-byte pack** is only
available while `Z_EROFS_ADVISE_COMPACTED_2B` is set in `h_advise`.
The two pack modes are named by their amortized size per logical cluster entry, as
described in the table below:

| Pack mode | Entries/Pack | Bits/Entry | Pack Size (in Bytes)    | Amortized Size/Entry |
|-----------|-------------:|-----------:|-------------------------|----------------------|
| 4-byte    | 2            | 16         | `(2 * 16 + 32) / 8 = 8`  | 4 |
| 2-byte    | 16           | 14         | `(16 * 14 + 32) / 8 = 32`| 2 |

As described, 4-byte packs need 8-byte alignment while 2-byte packs need 32-byte alignment. When `Z_EROFS_ADVISE_COMPACTED_2B` is **not set**, all entries use 4-byte packs.

Otherwise, when `Z_EROFS_ADVISE_COMPACTED_2B` is **set**, the stream is split into three
contiguous regions, where the middle 2-byte region is 32-byte aligned:

```
 ,--(8-byte aligned)    ,--(32-byte aligned)
 |                      |
 +----------------------+------------------+--------------+
 | 4B packs ...         | 2B packs ...     | 4B packs ... |
 +----------------------+------------------+--------------+
  (initial region)      (middle region)    (trailing)
```

The initial region pads any entries that do not satisfy the 32-byte alignment
requirement for the middle region.
The trailing region handles remaining entries that do not fill a complete
16-entry 2-byte pack.

### Per-inode Compression Features

Several optional features can be enabled on a per-inode basis through bits of
the `h_advise` field in the compression map header:

- **Ztailpacking** — keeps small tail data inline within the inode metadata block,
  avoiding a separate block allocation.
- **Big Physical Cluster** — allows a single pcluster to span more than one block,
  increasing compression granularity.
- **Interlaced Physical Cluster** — stores PLAIN pcluster data as a circular buffer
  within the block.
- **Tail-fragment Mode** — redirects the last logical cluster into a shared packed
  inode rather than a dedicated compressed block.
- **All-fragments Mode** — stores the entire file as a single fragment in the packed
  inode, replacing the map header and cluster index entirely.
- **Encoded Extents** — replaces the logical cluster index with a compact,
  position-keyed extent array (`EROFS_INODE_COMPRESSED_FULL` only).

#### Ztailpacking

When `Z_EROFS_ADVISE_INLINE_PCLUSTER` is set, `h_idata_size` bytes of inline tail
data are stored immediately after the last logical cluster index entry, within the
same metadata block as the inode. This avoids a separate block allocation for small
tail extents.

(big-physical-cluster)=
#### Big Physical Cluster

Per-inode, `Z_EROFS_ADVISE_BIG_PCLUSTER_1` or `Z_EROFS_ADVISE_BIG_PCLUSTER_2`
in `h_advise` indicate that HEAD1 or HEAD2 pclusters respectively may span **more
than one** block. Requires `EROFS_FEATURE_INCOMPAT_BIG_PCLUSTER`.

When active, the big pcluster's size is conveyed through the first NONHEAD entry
that follows: when `Z_EROFS_LI_D0_CBLKCNT` (bit 11) is set in its `di_advise`,
`di_u.delta[0]` carries the pcluster's compressed block count rather than the usual
distance to the HEAD lcluster (which is implicitly 1 in this case).

#### Interlaced Physical Cluster

When `Z_EROFS_ADVISE_INTERLACED_PCLUSTER` is **not** set, PLAIN pclusters use
the default layout: logical data starts at byte `di_clusterofs`
within the physical block, leaving the leading bytes wasted.

```
Physical block (default layout):

  0        di_clusterofs                           blksize
  +--------+-----------------------------------------+
  | wasted |   data[0 .. blksize - di_clusterofs)    |
  +--------+-----------------------------------------+
```

When `Z_EROFS_ADVISE_INTERLACED_PCLUSTER` is set, all PLAIN (uncompressed)
pclusters use the **interlaced layout**: the block is treated as a circular
buffer with `di_clusterofs` as the cut point, so no bytes are wasted.

```
Physical block (interlaced layout):

  0           di_clusterofs                     blksize
  +-----------+-----------------------------------+
  | data tail |           data head               |
  +-----------+-----------------------------------+
```
- `block[di_clusterofs .. blksize)` holds `data[0 .. blksize - di_clusterofs)` -- the leading bytes of logical data (head).
- `block[0 .. di_clusterofs)` holds `data[blksize - di_clusterofs .. blksize)` -- the remaining bytes (tail).

(fragment-mode)=
#### Fragment Mode

When `Z_EROFS_ADVISE_FRAGMENT_PCLUSTER` is set in `h_advise`, part or all of the
file's data is stored as a fragment within a shared packed inode rather than in
dedicated compressed blocks. Two mutually exclusive sub-modes exist, selected by
bit 7 of `h_clusterbits` (`Z_EROFS_FRAGMENT_INODE_BIT`):

- **Tail-fragment Mode** — only the tail of the file is a fragment; the rest
  is described normally by the logical cluster index.
- **All-fragments Mode** — the entire file is a single fragment; the map
  header and cluster index are replaced entirely.

##### Tail-fragment Mode

When `Z_EROFS_FRAGMENT_INODE_BIT` is **not** set in `h_clusterbits`, the tail of the
file (the last logical cluster) is stored as a fragment within the packed inode
rather than in a dedicated compressed block. The rest of the file is described
normally by the logical cluster index that follows the map header.

- `h_fragmentoff` (offset 0x00, 32 bits) gives the byte offset of the tail fragment
  within the packed inode's data region.
- `h_advise`, `h_algorithmtype`, `h_clusterbits`, and the lcluster index that follows
  the map header all retain their normal meanings.
- The fragment offset is limited to 32 bits, which is sufficient because the packed
  inode is not expected to exceed 4 GiB.

(all_fragments_mode)=
##### All-fragments Mode

When `Z_EROFS_FRAGMENT_INODE_BIT` is set in `h_clusterbits`, the entire
file's data is stored as a single fragment within the packed inode and the
normal map header structure is abandoned entirely. The 8-byte map header
region is reinterpreted as a single little-endian 64-bit integer:

| Bits | Name                         | Description |
|------|------------------------------|-------------|
| 63   | `Z_EROFS_FRAGMENT_INODE_BIT` | Always 1; marks this inode as all-fragments |
| 0–62 | fragment offset              | Byte offset of the file's complete data within the packed inode's data region |

In this mode there is no `h_advise`, no `h_algorithmtype`, no `h_clusterbits`,
and no logical cluster index follows the map header. Note that bit 7 of
`h_clusterbits` — i.e. `Z_EROFS_FRAGMENT_INODE_BIT` — is also bit 63 of the
entire 8-byte map header region interpreted as a little-endian `u64`.

(encoded_extents)=
#### Encoded Extents Mode

TBD.
