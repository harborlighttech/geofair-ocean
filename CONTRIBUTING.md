# Contributing

## Suggesting a resource (anyone)

Use the **Suggest a resource** Issue form in this repository. A workflow converts it into a pull request; a maintainer reviews and publishes it.

## Adding or editing a resource file (maintainers)

Resources are Markdown files in `_resources/`. Every resource has an author-assigned **local identifier** (`local_id`: letters, digits, `.`, `-`, `_`; unique in the catalogue, case-insensitively), and the file is named after it — `<local_id>.md` or `<local_id>-<slug>.md` — which makes the identifier the start of the resource's URL (`/resources/<local_id>-<slug>/`). The front matter is the record; the Markdown body is optional notes shown on the page.

### Field reference

| Field | Required | Type | RDA element | Notes |
| --- | --- | --- | --- | --- |
| `local_id` | yes | `[A-Za-z0-9._-]+`, ≤ 64 chars | — | author-assigned, unique; filename must start with it |
| `title` | yes | string ≤ 1000 | Title | as on the resource |
| `description` | yes | string 40–2000 | Abstract / Description | plain text |
| `resource_url` | yes | URL | URL to Resource | landing page or PID |
| `url_type` | no | `URL` `DOI` `Handle` `ARK` `PURL` `URN` | Resource URL Type | inferred from the URL when omitted |
| `identifier` | no | URL | — | DOI/handle when `resource_url` is a plain page |
| `resource_type` | yes | id from `_data/vocab/resource_type.yml` | Learning Resource Type | single value |
| `license.id` | yes | SPDX id from `_data/licenses.yml` | License | e.g. `CC-BY-4.0` |
| `version_date` | yes | `YYYY-MM-DD` | Version Date | date of the current version of the resource |
| `authors[]` | no | `{name, type, orcid, ror, affiliation}` | Author(s) | `type` is `Person` or `Organization` |
| `language` | no (default `en`) | BCP 47 | Primary Language | |
| `keywords[]` | no | strings | Keyword(s) | facet labels are added automatically in the JSON-LD |
| `audience[]` | no | ids from `_data/vocab/audience.yml` | Target Group | |
| `learning_outcomes[]` | no | strings | Learning Outcome | one sentence each |
| `access_cost` | no (default `"no"`) | `"no"` `"yes"` `"maybe"` (ids from `_data/vocab/access_cost.yml`, shown as Free / Paid / May have a cost) | Access Cost | **quote the value**: an unquoted `no` is read as `false` |
| `expertise_level` | no | `beginner` `intermediate` `advanced` | Expertise Level | |
| `object_types[]` | no (derived from `resource_type` when omitted) | ids from `_data/vocab/object_type.yml` (DataCite `resourceTypeGeneral` values in kebab-case, e.g. `dataset`, `software`, `computational-notebook`, `text`) | — | one or more; emitted as `schema:additionalType` COAR URIs |
| `lifecycle_stages[]` | yes | ids from `_data/vocab/lifecycle_stage.yml` | — | one or more |
| `research_areas[]` | yes | ids from `_data/vocab/research_area.yml` | — | one or more |
| `status` | yes | `draft` `in-review` `published` `obsolete` | — | |
| `superseded_by` | no | `local_id` of another resource, or URL | — | for obsolete entries |
| `testimonials[]` | no | `{provider: {name, type, affiliation, url}, text, date}` | — | emitted as `schema:Review` |
| `image` | no | path or URL | — | optional thumbnail |
| `date_added` | no | `YYYY-MM-DD` | — | catalogue bookkeeping |

Run `python scripts/validate_resources.py` before opening a pull request; CI runs the same checks.

### Review checklist

- Description is accurate, neutral and within 2,000 characters.
- Lifecycle stages and research areas reflect what the resource teaches, not everything it mentions.
- Licence and version date verified on the resource itself.
- `resource_url` opens; a DOI or handle is used when one exists.
- Testimonials name a real provider who agreed to be quoted.
- `status: published` set before merging.

## Changing a vocabulary

Edit the file in `_data/vocab/`, keep ids stable (resources reference them), then run `python scripts/build_issue_form.py` and commit the regenerated Issue forms. To retire a term, remove it only after no resource uses it (`grep -r "term-id" _resources/`).

## Site changes

Layouts, includes, CSS and `facets.js` are plain Jekyll and vanilla JavaScript; there is no build step beyond `jekyll build`. Keep colours as CSS variables so `theme_colors` in `_config.yml` keeps working for other domains.
