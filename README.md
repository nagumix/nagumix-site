# NaguMIX site

This is the pre-publication scaffold for the future NaguMIX project site and
user documentation. It starts from the official OINK Starter and imports the
OINK Hugo Module at the version pinned in `go.mod`.

The scaffold is intentionally small. It does not claim that downloads, releases,
source repositories, support channels, or a hosted site exist. Deployment
workflows are deferred until destination URLs and hosting are approved.

## Local build

Requirements:

- Git
- Go 1.27 or newer
- Hugo Extended 0.165.0 or newer

Preview locally:

```console
hugo server
```

Run the warning-strict production build:

```console
hugo --cleanDestinationDir --gc --minify --environment production \
  --printPathWarnings --panicOnWarning
```

`baseURL` currently uses the reserved `example.invalid` domain. Replace it only
when the real public location is approved.

## Languages

English is the only enabled language. Simplified Chinese and French remain
declared but disabled so translated files can be added later without changing
the filename conventions. The starter's single- and bilingual-language examples
and interface translation structure are retained as reference inputs; sample
project prose is not.

## Licensing

Starter-derived site files retain the MIT license in `LICENSE`. The imported
OINK theme is Apache-2.0 and its license and NOTICE are under `LICENSES/`.
Original NaguMIX prose is CC-BY-SA-4.0. See `NOTICE.md` for the exact scopes.
