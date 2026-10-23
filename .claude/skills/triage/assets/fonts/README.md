# Bundled fonts

The renderer embeds these WOFF2 faces directly in each output, together with
copyright/licence notices. No font service is contacted.

| File                           | Face          | Weight |
| ------------------------------ | ------------- | ------ |
| `inter-display-semibold.woff2` | Inter Display | 600    |
| `inter-semibold.woff2`         | Inter         | 600    |
| `lato-regular.woff2`           | Lato          | 400    |

Sources: [Inter](https://github.com/rsms/inter) and
[Lato](https://www.latofonts.com/). These files are lossless WOFF2 conversions of
the full installed upstream faces; glyphs were not subsetted or modified.

`LICENSE-Inter.txt` and `LICENSE-Lato.txt` preserve the distribution's copyright
and licence records. Font software is covered by the SIL Open Font License 1.1
(with Apache 2.0 also recorded for Inter); Debian packaging entries are identified
separately in those records. These licences do not govern the rendered ticket content.
