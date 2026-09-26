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
- Go 1.27.0
- Hugo Extended 0.166.0
- Python 3.12 or newer (for rendered-link checks)

Preview locally:

```console
hugo server
```

Run the warning-strict production build:

```console
hugo --cleanDestinationDir --gc --minify --environment production \
  --printPathWarnings --panicOnWarning
```

Run the same validation as the CI definition, using separate destinations for
the root and reserved-domain subpath forms:

```console
GOTOOLCHAIN=local go mod download
GOTOOLCHAIN=local go mod verify
hugo mod tidy --environment production
git diff --exit-code -- go.mod go.sum
python -m unittest discover -s tests -v
hugo --cleanDestinationDir --gc --minify --environment production \
  --printPathWarnings --panicOnWarning --destination build/root
python scripts/check_rendered_links.py build/root --base-url https://example.invalid/
hugo --cleanDestinationDir --gc --minify --environment production \
  --printPathWarnings --panicOnWarning --baseURL https://example.invalid/nagumix-check/ \
  --destination build/subpath
python scripts/check_rendered_links.py build/subpath --base-url https://example.invalid/nagumix-check/
```

The checker follows local `href`, `src`, `poster`, and meta-refresh targets,
requires target files, and verifies HTML fragment IDs and named anchors. It
does not fetch external origins; `mailto:`, `tel:`, `data:`, `javascript:`, and
other non-HTTP schemes are intentionally ignored. The GitLab configuration
creates validation pipelines for branch pushes without an open merge request,
merge requests, and default-branch pushes after integration. It intentionally
excludes tags, schedules, API-triggered, and other pipeline sources.

| Pipeline source/context | Result |
| --- | --- |
| Branch push with no open merge request | validation pipeline |
| Merge request event | validation pipeline |
| Branch push with an open merge request | suppressed to avoid a duplicate MR pipeline |
| Default-branch push after integration | validation pipeline |
| Tag, schedule, API, trigger, web, or other source | no pipeline |

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
