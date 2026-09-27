# NaguMIX site

The NaguMIX site contains a product landing page, getting-started guide,
controls reference, availability information and a small FAQ. It uses the
official OINK Starter and the OINK Hugo Module pinned in `go.mod`.

Application source is available at https://github.com/nagumix/nagumix.
Packaged downloads are not yet available.

Home sections are configured in `data/home/en.yaml`; guide pages live under
`content/docs/`. The hero uses `static/images/nagumix-hero.webp`, a 960-pixel
transparent derivative. A small project SCSS extension keeps the artwork within
its square and lets the headline wrap on narrow screens. Branding terms are in
`NOTICE.md`.

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
creates validation pipelines and publishes one complete Pages snapshot. The
stable `main` branch occupies the Pages root. Every current branch is also built
at a deterministic path below `branches/`; a branch name is mapped to a readable
slug plus a digest of its complete ref name. The `branches/` output path is
therefore reserved for previews.

The publisher serializes updates, refreshes all branch tips after it starts, and
builds those exact commits as one artifact. A failed build leaves the previous
successful Pages deployment in place. A deleted branch disappears from the next
successful complete snapshot; the publisher never deletes repository branches.
Merge-request pipelines can publish only for branches in this project. Fork
merge requests remain validation-only and cannot run the Pages publisher.
Tags, schedules, API-triggered, and other pipeline sources are excluded.

| Pipeline source/context | Result |
| --- | --- |
| Branch push with no open merge request | validation and one aggregate Pages publisher |
| Same-project merge request event | validation and one aggregate Pages publisher |
| Branch push with an open merge request | branch pipeline suppressed; the MR pipeline refreshes Pages |
| Fork merge request event | validation only |
| Default-branch push after integration | validation and one aggregate Pages publisher |
| Tag, schedule, API, trigger, web, or other source | no pipeline |

`baseURL` remains the safe local default `example.invalid`. CI overrides it for
each build with that output's effective Pages URL; reserved-domain validation
output is never deployed.

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
