# GeoFAIR Ocean Resource Hub

A Jekyll site for GitHub Pages that catalogues learning and training resources for FAIR ocean data, with a faceted search page driven by Schema.org JSON-LD. Each resource is one Markdown file whose front matter follows the [RDA Minimal Metadata for Learning Resources](https://doi.org/10.15497/RDA00073) plus four GeoFAIR facets (lifecycle stage, resource type, research area, status) and testimonials.

This repository is the **Ocean** instance of the GeoFAIR Resource Hub template. Other domains copy it and change the first block of `_config.yml` and the vocabularies.

## Set up a new instance

1. **Create the repository** from this ZIP (or use it as a template) and push to GitHub.
2. **Edit the top of `_config.yml`**: `title`, `domain`, `tagline`, `organization`, `url`, `baseurl`, `github_repo`, `footer_links`, and the `theme_colors` block. Every `TODO` in that file needs a value.
   - Project site (`https://<org>.github.io/<repo>/`): `url: https://<org>.github.io`, `baseurl: /<repo>`.
   - Organisation site or custom domain: `baseurl: ""`.
3. **Repository settings → Pages**: set *Source* to **GitHub Actions**.
4. **Repository settings → Actions → General → Workflow permissions**: choose *Read and write permissions* and tick *Allow GitHub Actions to create and approve pull requests* (needed by the Issue-form workflow).
5. Replace `@example-owner` in `.github/CODEOWNERS`.
6. **Replace the sample resources** in `_resources/` (all start with `sample-`) with real ones, then push. The first push to `main` builds and deploys.
7. Review the vocabularies in `_data/vocab/` (see below) and fill in the `same_as` links marked `TODO`.

## Look and feel: colours, fonts, logo

The visual language follows the AGU *Impactful Datasets* site: Montserrat for headings, labels, navigation and buttons; Lora for running prose; AGU brand colours (#244C5A primary, #007DBA secondary) on white; hairline rules and 6 px cards. All of it is configured in `_config.yml`:

- `theme_colors:` — each value becomes a CSS custom property (`--c-primary`, `--c-accent`, …) in every page's `<head>`; `assets/css/site.css` only ever references those variables, so a domain restyles the site without touching CSS. Keep text/background contrast at 4.5:1 or better.
- `fonts:` — `display` and `body` font stacks (emitted as `--f-display` / `--f-body`) and `google_fonts_url`, which loads the web fonts. Set `google_fonts_url: ""` to avoid the external request; the stacks then fall back to system fonts.
- `logo:` — optional. A path inside the site (`assets/img/logo.png`) or an absolute `https://` URL. When set, the image is shown in the header immediately before the site title at `logo_height` px (width scales); `logo_alt` is its accessible name. When empty, nothing is rendered in that space.

## Repository layout

```
_config.yml                 site settings, colours, navigation, catalogue behaviour
_resources/                 one Markdown file per resource (front matter = the record)
_data/vocab/*.yml           controlled vocabularies (facets); one file per vocabulary
_data/licenses.yml          SPDX licence ids accepted in resources
_layouts/                   default, resource (page + JSON-LD), vocab (DefinedTermSet page)
_includes/jsonld/resource.html   the single JSON-LD template used by every output
_includes/jsonld/term.html       one DefinedTerm
_includes/facet-panel.html  facet checkboxes rendered from the vocabularies
resources/index.html        faceted search page (embedded ItemList + <noscript> list)
resources.jsonld            the same ItemList as a standalone file
vocab/                      one page per vocabulary
assets/css/site.css         styles (colours via CSS variables)
assets/js/facets.js         client-side faceting, no dependencies
schema/resource.schema.json JSON Schema for resource front matter
schema/geofair-shapes.ttl   SHACL shapes for the emitted JSON-LD (optional check)
scripts/                    validators, Issue-form generator, issue-to-resource converter
.github/workflows/pages.yml       validate → build → validate JSON-LD → deploy
.github/workflows/issue-to-pr.yml Issue form → resource file → pull request
.github/ISSUE_TEMPLATE/     generated forms (do not edit by hand)
```

## Adding a resource

Contributors use the **Suggest a resource** Issue form; the workflow turns it into a pull request with `status: in-review`. Maintainers review, set `status: published`, and merge. Maintainers can also add a file to `_resources/` directly; `CONTRIBUTING.md` has the field reference.

Every resource carries an author-assigned `local_id` (letters, digits, `.`, `-`, `_`), unique across the catalogue; the file is named `<local_id>_<slug>.md` and the **canonical** page URL is `/resources/<local_id>/` (set from the front matter by `_plugins/resource_alias.rb`, not from the filename). Every link on the site uses the readable form `/resources/<local_id>/<slug>/` (slug from the filename, or an explicit `slug` field), which `_plugins/resource_alias.rb` builds as a full copy of the page declaring the canonical URL in `<link rel="canonical">` and the JSON-LD `@id`. Because the identifier is what matters, a wrong or misspelled slug still resolves: `404.html` redirects any `/resources/<local_id>/<anything>` to `/resources/<local_id>/`. The plugin runs in the Actions build and in local `jekyll build`, but not under the GitHub Pages default builder (which runs `--safe`). CI rejects a missing, malformed or duplicate identifier, a filename that does not match it, and a build missing any alias page.

A resource file whose name starts with `_` (e.g. `_resources/_wip-id.md`) is skipped by the build entirely; `_resources/_template.md` is a skipped template to copy from.

Status rules: `draft` and `in-review` pages are built (so reviewers can preview them) but carry `noindex` and never enter the search index; `published` entries are listed; `obsolete` entries are indexed but hidden on the search page until the visitor ticks *Include obsolete*.

## Vocabularies

Each file in `_data/vocab/` has the same shape (`id`, `name`, `description`, `field`, `cardinality`, `terms[]` with `id`, `label`, `definition`, optional `same_as`, `broad_match`, `close_match`). Resources reference term **ids**. The search page, resource pages, vocabulary pages, Issue forms and validator all read these files, so a term is added in one place.

After changing a vocabulary, regenerate the Issue forms and commit them:

```
python scripts/build_issue_form.py
```

CI fails if the committed forms are stale.

The research-area list for this instance is based on the NASA GCMD Earth Science Keywords under *Oceans*; the `same_as` entries are left empty for the domain owner to fill with GCMD concept URIs.

`object_type.yml` is the DataCite 4.7 `resourceTypeGeneral` list with COAR Resource Types 3.2 and DCMI Type crosswalks; a resource's `object_types` become `schema:additionalType` values (COAR URI, else DCMI URI, else the DataCite value) and an "Object type" facet.

## Local development

```
bundle install
bundle exec jekyll serve --livereload      # http://localhost:4000/<baseurl>/
pip install -r requirements.txt
python scripts/validate_resources.py       # front matter, vocab ids, licences
python scripts/test_validation.py          # validator self-test against _resources/_test-*.md fixtures
python scripts/validate_jsonld.py          # after a build: parses and checks every JSON-LD block
python scripts/validate_jsonld.py --shacl  # optional; needs pyshacl and rdflib
```

## Structured data

Every resource page embeds one `schema:LearningResource` (conforming to the Bioschemas TrainingMaterial 1.0 profile) with vocabulary values as `schema:DefinedTerm` objects whose `inDefinedTermSet` is this site's vocabulary URL, testimonials as `schema:Review`, and status as `creativeWorkStatus`. The search page embeds one `schema:ItemList` of the same objects, generated by the same include, and `/resources.jsonld` is that list as a file for harvesters.

## Licence

Site code: MIT (see `LICENSE`). Catalogue metadata: CC BY 4.0. Each catalogued resource keeps its own licence.
