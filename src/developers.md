# 📚 Developer Guides

## Git Repositories

### erofs-utils

erofs-utils is developed with [Git](https://git-scm.com), and multiple branches
are available for different needs:

```sh
$ git clone git://git.kernel.org/pub/scm/linux/kernel/git/xiang/erofs-utils.git
```

| branch       | description                                         | rebase? |
| ------------ | --------------------------------------------------- | ------- |
| dev          | erofs-utils development tree                        |  Maybe  |
| experimental | erofs-utils tree with unstable patches for testing  |    Yes  |
| master       | erofs-utils stable tree                             |     No  |

### Linux kernel source
If you're interested in EROFS kernel development, it is recommended to keep
your local code in sync with the latest [EROFS development repo](https://git.kernel.org/pub/scm/linux/kernel/git/xiang/erofs.git):

```sh
$ git clone git://git.kernel.org/pub/scm/linux/kernel/git/xiang/erofs.git
```

| branch       | description                                         | rebase? |
| ------------ | --------------------------------------------------- | ------- |
| fixes        | EROFS kernel fixes-only tree (for this cycle)       |    Yes  |
| dev          | EROFS kernel development tree (for the next cycle)  |    Yes  |

## Mailing List

EROFS has its own development mailing list hosted by [OzLabs](https://www.ozlabs.org):
<[linux-erofs@lists.ozlabs.org](mailto:linux-erofs@lists.ozlabs.org)>

You can [subscribe to the mailing list](https://lists.ozlabs.org/listinfo/linux-erofs)
to receive the latest status of EROFS.

When posting, it is helpful to:

 - Add an additional tag in the subject like `[PATCH]`, `[question]` or
`[bug report]`, etc.;

 - Avoid [top-posting](https://daringfireball.net/2007/07/on_top) if possible.

All patches should follow the Linux kernel's coding style. Additionally, as
one of the Linux kernel development communities, patches require the "sign-off"
procedure.

The sign-off should be appended as a simple line at the end of the commit
message for the patch, which claims that you agree to [Developer Certificate of Origin](https://developercertificate.org/).
In other words, it certifies that either you wrote it or have the right to pass
it on as an open-source patch.

Then you just add a line saying:

```
	Signed-off-by: Random J Developer <random@developer.example.org>
```

using your real name (sorry, no pseudonyms or anonymous contributions.)

## Matrix room

You can also join our Matrix room
([#erofs:matrix.org](https://matrix.to/#/#erofs:matrix.org)) for informal
discussions.

However, proposals, bug reports, and/or patches should be sent to the mailing
list eventually so that they can be properly archived.
