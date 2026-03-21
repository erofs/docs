(xattrs)=
# Extended Attributes (Xattrs)

EROFS supports Extended Attributes
([xattr(7)](https://man7.org/linux/man-pages/man7/xattr.7.html)) which are
`name:value` pairs associated permanently with inodes since the initial Linux
5.4 version.

## Superblock Fields for Xattr Support

The core superblock format is defined in {ref}`on_disk_superblock`. This
section lists the extended fields dedicated to the xattr features.

| Offset | Size | Type  | Name                     | Description |
|--------|------|-------|--------------------------|-------------|
| 0x08   | 4    | `u32` | `feature_compat`         | Compatible feature flags; see {ref}`xattr_feature_flags` |
| 0x2C   | 4    | `u32` | `xattr_blkaddr`          | Start block address of the shared xattr area; see {ref}`shared_xattr_area` |
| 0x50   | 4    | `u32` | `feature_incompat`       | Incompatible feature flags; see {ref}`xattr_feature_flags` |
| 0x5B   | 1    | `u8`  | `xattr_prefix_count`     | Number of long xattr name prefixes; valid when `EROFS_FEATURE_INCOMPAT_XATTR_PREFIXES` is set; see {ref}`long_xattr_prefixes` |
| 0x5C   | 4    | `u32` | `xattr_prefix_start`     | Location of the long xattr prefix table; valid when `EROFS_FEATURE_INCOMPAT_XATTR_PREFIXES` is set; see {ref}`long_xattr_prefixes` |
| 0x60   | 8    | `u64` | `packed_nid`             | Packed inode NID. Relevant when long xattr prefixes are embedded in the packed inode's data region |
| 0x68   | 1    | `u8`  | `xattr_filter_reserved`  | Must be 0 for the xattr Bloom filter to operate; see {ref}`xattr_filter` |
| 0x69   | 1    | `u8`  | `ishare_xattr_prefix_id` | Long-prefix table index used by image-share xattrs; valid when both `EROFS_FEATURE_COMPAT_ISHARE_XATTRS` and `EROFS_FEATURE_INCOMPAT_XATTR_PREFIXES` are set; see {ref}`image_share_xattrs` |
| 0x80   | 8    | `u64` | `metabox_nid`            | Metabox inode NID. Relevant when shared xattrs or long xattr prefixes are stored in the metabox inode's data region |

(xattr_feature_flags)=
## Xattr Feature Flags

The following superblock feature bits are directly relevant to xattr support.

### `feature_compat` Bits

| Bit mask     | Name                                        | Description |
|--------------|---------------------------------------------|-------------|
| `0x00000004` | `EROFS_FEATURE_COMPAT_XATTR_FILTER`         | Enables the per-inode xattr Bloom filter described in {ref}`xattr_filter` |
| `0x00000008` | `EROFS_FEATURE_COMPAT_SHARED_EA_IN_METABOX` | Stores the shared xattr area in the metabox inode's decoded data region instead of at `xattr_blkaddr` |
| `0x00000010` | `EROFS_FEATURE_COMPAT_PLAIN_XATTR_PFX`      | Stores the long xattr prefix table as a standalone region; valid when `EROFS_FEATURE_INCOMPAT_XATTR_PREFIXES` is set; see {ref}`long_xattr_prefixes` |
| `0x00000020` | `EROFS_FEATURE_COMPAT_ISHARE_XATTRS`        | Enables image-share xattrs. `ishare_xattr_prefix_id` is valid only when this bit and `EROFS_FEATURE_INCOMPAT_XATTR_PREFIXES` are both set; see {ref}`image_share_xattrs` |

### `feature_incompat` Bits

| Bit mask     | Name                                 | Description |
|--------------|--------------------------------------|-------------|
| `0x00000040` | `EROFS_FEATURE_INCOMPAT_XATTR_PREFIXES` | Enables the long xattr prefix table described in {ref}`long_xattr_prefixes` |

(xattr_inode_fields)=
## Inode Fields for Xattr Support

The full compact and extended inode layouts are defined in {ref}`on_disk_inodes`.
For xattr support, both inode variants share the same feature-specific field:

| Offset | Size | Type  | Name             | Description |
|--------|------|-------|------------------|-------------|
| 0x02   | 2    | `u16` | `i_xattr_icount` | When non-zero, the inline xattr region size is `(i_xattr_icount - 1) * 4 + 12` bytes |

Two storage classes exist:

- **Inline xattrs**: stored directly in the metadata block immediately following
  the inode body (and any inline data tail). They are private to the inode and
  encoded as a sequence of xattr entry records within the inline xattr region
  described by `i_xattr_icount`.
- **Shared xattrs**: stored once in the global shared xattr area. An inode references
  a shared entry through a 4-byte index stored immediately after the fixed
  12-byte inline xattr header.
  Multiple inodes that carry an identical xattr (same name and value) can reference
  the same shared entry, avoiding redundant per-inode copies.

To further reduce storage overhead for xattrs whose names share a common prefix
(for example `trusted.overlay.*` or `security.ima.*`), EROFS supports a long xattr
prefix table (`EROFS_FEATURE_INCOMPAT_XATTR_PREFIXES`). Each prefix entry records a
`base_index` that refers to one of the standard short namespace prefixes and an
additional infix string. An xattr entry whose `e_name_index` selects a long prefix
stores only the suffix that follows the full reconstructed prefix, rather than
repeating the prefix in every entry.

(inline_xattr_region)=
## Inline Xattr Region Layout

The inline xattr region immediately follows the inode body (at a 4-byte aligned
offset). Its total size is `(i_xattr_icount - 1) * 4 + 12` bytes, where 12 is the
fixed size of the inline xattr body header. The region is structured as:

1. The {ref}`inline_xattr_body_header` (12 bytes, fixed).
2. `h_shared_count` × 4-byte shared xattr index values.
3. Zero or more {ref}`xattr_entry_record` (inline entries).

(inline_xattr_body_header)=
### Inline Xattr Body Header

| Offset | Size | Type   | Name             | Description |
|--------|------|--------|------------------|-------------|
| 0x00   | 4    | `u32`  | `h_name_filter`  | Inverted Bloom filter over xattr names; valid when `EROFS_FEATURE_COMPAT_XATTR_FILTER` is set; see {ref}`Xattr Filter <xattr_filter>` |
| 0x04   | 1    | `u8`   | `h_shared_count` | Number of shared xattr index entries |
| 0x05   | 7    | `u8[]` | _reserved_       | Reserved; must be 0 |

(xattr_entry_record)=
### Xattr Entry Record

Each inline or shared xattr entry has the following layout:

| Offset | Size | Type  | Name           | Description |
|--------|------|-------|----------------|-------------|
| 0x00   | 1    | `u8`  | `e_name_len`   | Length of the name suffix in bytes |
| 0x01   | 1    | `u8`  | `e_name_index` | Namespace index (maps to a prefix string); see below |
| 0x02   | 2    | `u16` | `e_value_size` | Length of the value in bytes |

Immediately following the 4-byte xattr entry header: `e_name_len` bytes of name
suffix, then `e_value_size` bytes of value. The entire entry (header + name + value)
is padded to a 4-byte boundary.

(e_name_index-namespace-mapping)=
#### `e_name_index` Namespace Mapping

Rather than storing the full namespace prefix string in every entry, EROFS encodes
the xattr namespace prefix as a 1-byte index. Bit 7 of `e_name_index` is the
`EROFS_XATTR_LONG_PREFIX` flag. When set, the lower 7 bits index into the long
xattr name prefix table (see {ref}`long_xattr_prefixes`).
When clear, the full byte selects one of the built-in short namespace prefixes:

| Value | Prefix |
|-------|--------|
| 1     | `user.` |
| 2     | `system.posix_acl_access` |
| 3     | `system.posix_acl_default` |
| 4     | `trusted.` |
| 6     | `security.` |

All other `e_name_index` values (including `0` and `5`) are reserved and must not be used unless defined by a future format extension.
(shared_xattr_area)=
## Shared Xattr Area

Normally, the shared xattr area begins at block address `xattr_blkaddr`. Each shared
entry is an xattr entry record stored contiguously in this area. An inode references
a shared entry by its 32-bit index, stored in the inline xattr region immediately
after the 12-byte inline xattr header. The index is a byte offset within the
shared area divided by 4.

When `EROFS_FEATURE_COMPAT_SHARED_EA_IN_METABOX` is set, the shared xattr pool is
stored in the metabox inode's decoded data region rather than at `xattr_blkaddr`.

(long_xattr_prefixes)=
## Long Xattr Name Prefixes

This section applies when `EROFS_FEATURE_INCOMPAT_XATTR_PREFIXES` is set.

When this feature is set, a table of `xattr_prefix_count` prefix entries is
present; see {ref}`xattr_prefix_table_placement` for where that table is stored.
Each entry has the following fixed header. The full entry, including the
variable-length `infix` payload, is padded to a 4-byte boundary.

| Offset | Size | Type  | Name         | Description |
|--------|------|-------|--------------|-------------|
| 0x00   | 2    | `u16` | `size`       | Byte length of the following content: `base_index` plus the variable-length `infix` payload |
| 0x02   | 1    | `u8`  | `base_index` | Built-in short namespace prefix index (see {ref}`e_name_index-namespace-mapping`) |

The variable-length `infix` bytes begin at offset `0x03`. Their length is
`size - 1`, and they are not null-terminated.

The full reconstructed prefix is the concatenation of the short prefix indicated by
`base_index` and the `infix` bytes. An xattr entry using a long prefix stores only
the name suffix after the reconstructed prefix; `e_name_len` counts only those suffix
bytes.

For example, an xattr named `trusted.overlay.opaque` can be represented with
`base_index = 4` (`trusted.`) and `infix = "overlay."`, yielding the full prefix
`trusted.overlay.`; the stored name suffix is `opaque` with `e_name_len = 6`.

(xattr_prefix_table_placement)=
### Prefix Table Placement

The xattr prefix table start offset is recorded in `xattr_prefix_start`.
The table may be:
- embedded in the metabox or packed inode's data region when `EROFS_FEATURE_COMPAT_PLAIN_XATTR_PFX` is not set; or
- stored in a standalone region when `EROFS_FEATURE_COMPAT_PLAIN_XATTR_PFX` is set.

(xattr_filter)=
## Xattr Filter

This section applies when `EROFS_FEATURE_COMPAT_XATTR_FILTER` is set.

When this feature is set, `h_name_filter` in the inline xattr body header holds a
32-bit inverted Bloom filter over the inode's xattr names. Each bit position
corresponds to one hash bucket:

- A bit value of **1** guarantees that no xattr present on this inode hashes to that
  bucket, so the queried name is **definitely absent**.
- A bit value of **0** means a matching xattr **may exist** and a full scan is
  required.

When `xattr_filter_reserved` in the superblock is non-zero, the Bloom filter is
disabled unconditionally for all inodes in the image.

(image_share_xattrs)=
## Image-share Xattrs

This section applies when both `EROFS_FEATURE_COMPAT_ISHARE_XATTRS` and
`EROFS_FEATURE_INCOMPAT_XATTR_PREFIXES` are set.

When these features are set, the superblock field `ishare_xattr_prefix_id` is valid
and identifies an entry in the long xattr prefix table. Regular files may carry an
xattr whose name equals the prefix identified by `ishare_xattr_prefix_id`
(i.e. `e_name_index` selects that entry and `e_name_len` is 0) and whose value is
a SHA-256 content fingerprint in the form `sha256:<hex-digest>`.

This convention enables tools to identify files with identical content across
different EROFS images by comparing these fingerprints.
