# Integration

Use the actual weight of each font file. The current face has weight 800.

```css
@font-face {
  font-family: "dotmemo mijote";
  src: url("dotmemo-mijote-Bold.woff2") format("woff2");
  font-weight: 800;
  font-style: normal;
  font-display: swap;
}
.sample {
  font-family: "dotmemo mijote", sans-serif;
  font-weight: 800;
  font-synthesis: none;
}
```

Check the generated coverage inventory before selecting fallback fonts. Test
normalization, combining marks, mixed text, line breaks, selection, input, zoom,
cache updates and offline loading in target applications. Test installation,
family/style selection and PDF export separately on each supported platform.

Measure complete resources before subsetting. Subsets must preserve required
combining marks and OpenType dependencies. A fallback glyph does not establish
coverage by this font. Confirm distribution and embedding terms before deployment.
