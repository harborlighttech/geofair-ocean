# GeoFAIR Resource Hub — Jekyll Faceted Resource Catalog: Proposal

Nov 6, 2026 · @Adam Shepherd

## Summary

The GeoFAIR Resource Hub is a Jekyll site on GitHub Pages that catalogues external learning and training resources, one Markdown file per resource, and offers a faceted search page driven entirely by Schema.org JSON-LD generated at build time. Each resource's front matter is an application profile of the RDA *Minimal Metadata for Learning Resources* (all 14 elements present, 6 required) extended with four GeoFAIR facets (lifecycle stage, resource type, research area, status) and testimonials. Jekyll renders every resource page with a `schema:LearningResource` JSON-LD block (testimonials as `schema:Review`, vocabulary terms as `schema:DefinedTerm`), and the search page embeds one `schema:ItemList` of those same objects, which a small dependency-free script filters client-side. No Jekyll plugins are needed; the site builds in GitHub Actions, where a validation step checks every resource against a JSON Schema before deploy, and contributors add resources through a GitHub Issue form that opens a pull request.

Key design decisions, from your answers:

| Decision | Choice |
| --- | --- |
| What is catalogued | External learning/training materials; every entry is a `schema:LearningResource` and links out via RDA *URL to Resource* |
| RDA coverage | All 14 elements in the schema; Title, Description, URL, Resource Type, License, Version Date required; the rest optional with defaults |
| Controlled vocabularies | Survey existing vocabularies first (DataCite, LRMI, USGS, NASA GCMD, OECD, Schema.org); adopt, map or create per facet — candidates and a recommendation are in the vocabulary section |
| Cardinality | Lifecycle stage and research area multi-valued; resource type and status single-valued |
| Testimonials | `schema:Review` with `reviewBody` and `author` (Person or Organization) |
| Status | Draft, In Review, Published, Obsolete via `schema:creativeWorkStatus`; Draft and In Review build but are excluded from the search index and marked `noindex`; Obsolete is shown but filtered out until the visitor opts in |
| Identifiers | Resource page URL is the record's `@id`; the described material's own DOI/handle goes in `identifier` and `url` |
| Build | GitHub Actions (Jekyll 4.x, no third-party plugins needed, CI validation) deploying to GitHub Pages |
| Search | Client-side JS facets plus keyword box over the embedded JSON-LD; `<noscript>` fallback lists all published resources grouped by lifecycle stage |
| Authoring | GitHub Issue form with dropdowns generated from the vocabulary files; an Action turns the issue into a Markdown file and opens a PR |
| Site | New repository and theme; base URL placeholder `https://<org>.github.io/<repo>/` until the repo exists |

## Decisions taken and items still open

Eleven questions were asked and answered on 2026-11-06; the answers are folded into the Summary table above. The items below were not asked because they do not change the architecture, but each needs an answer before the matching implementation phase.

| Open item | Default assumed in this plan | Needed by |
| --- | --- | --- |
| Repository name and GitHub organisation (sets `url` and `baseurl` in `_config.yml`, and every `@id`) | `https://<org>.github.io/<repo>/` | Phase 1 |
| Vocabulary choice per facet (adopt, map, or create) after reviewing the candidates section | Recommendations in the vocabulary section | Phase 1 |
| Does GeoFAIR mean geoscience specifically? Decides whether research area uses an Earth-science scheme (NASA GCMD, USGS) or a general one (OECD FOS) | Geoscience | Phase 1 |
| Default license for resources whose license is unknown | Field left empty and flagged by CI, not defaulted | Phase 2 |
| Who may approve PRs from the Issue form (CODEOWNERS) | Repository owner | Phase 4 |
| Target audience and expertise-level term lists | Audience: researcher, data steward/manager, student, educator, repository or infrastructure staff, policy maker. Level: beginner, intermediate, advanced | Phase 1 |
| Should testimonials show the provider's affiliation and a link, or name only? | Name, optional affiliation, optional URL; all shown if present | Phase 2 |
| Keyword field: free text or constrained? | Free text, lower-cased, plus the vocabulary terms copied in automatically for discovery | Phase 2 |
| Analytics or search logging on the search page | None (static site, no third-party scripts) | Phase 3 |
| Theme | A lightweight accessible theme (e.g. a minimal custom layout with no theme gem, or `just-the-docs` if a docs-style sidebar is wanted) | Phase 1 |

## Resource schema for Jekyll

Each resource is one Markdown file in a `_resources` collection; its YAML front matter is the record, and the four vocabularies live as YAML files under `_data/vocab/` so that layouts, the Issue form and CI validation all read the same term lists. Field names are snake\_case; vocabulary fields hold term *ids* (slugs), never labels, so labels can be edited without touching resources.

| Field | Type | Required | RDA element | Notes |
| --- | --- | --- | --- | --- |
| `title` | string ≤ 1000 chars | Yes | Title | Transcribed from the resource |
| `description` | string ≤ 2000 chars | Yes | Abstract / Description | Your "descriptive context" field. Longer narrative goes in the Markdown body, which renders on the page but is not emitted as metadata |
| `url` | URL | Yes | URL to Resource | Landing page or persistent identifier of the external material |
| `url_type` | enum: `URL`, `DOI`, `Handle`, `ARK`, `PURL`, `URN` | No (auto-detected) | Resource URL Type | Subset of DataCite `relatedIdentifierType`; CI infers `DOI` from `doi.org`, `Handle` from `hdl.handle.net` |
| `resource_type` | one term id from `resource_type` vocab | Yes | Learning Resource Type | Single-valued |
| `license` | object `{id, name, url}` | Yes | License | `id` is an SPDX identifier (e.g. `CC-BY-4.0`); `name` and `url` filled from `_data/licenses.yml` when omitted |
| `version_date` | ISO 8601 date | Yes | Version Date | Date of the most recent version of the external resource, not of the catalogue entry |
| `authors` | list of `{name, type, orcid, ror, affiliation}` | No | Author(s) | `type` is `Person` or `Organization`; ORCID/ROR optional |
| `language` | BCP 47 / ISO 639-1 code | No, default `en` | Primary Language | One record per language version, per RDA guidance |
| `keywords` | list of strings | No | Keyword(s) | Free text; vocabulary labels are appended automatically in the JSON-LD |
| `audience` | list of term ids from `audience` vocab | No | Target Group (Audience) | Small local list (see vocabularies) |
| `learning_outcomes` | list of strings | No | Learning Outcome | One sentence each |
| `access_cost` | enum `no`, `yes`, `maybe` | No, default `no` | Access Cost | `maybe` must be explained in `description` |
| `expertise_level` | enum `beginner`, `intermediate`, `advanced` | No | Expertise Level | Bioschemas/TeSS convention |
| `lifecycle_stages` | list of term ids, ≥ 1 | Yes | — (GeoFAIR facet) | Multi-valued |
| `research_areas` | list of term ids, ≥ 1 | Yes | — (GeoFAIR facet) | Multi-valued |
| `status` | one term id: `draft`, `in-review`, `published`, `obsolete` | Yes | — (GeoFAIR facet) | Issue form sets `in-review`; maintainer sets `published` at merge |
| `superseded_by` | URL or resource slug | No | — | Only meaningful when `status: obsolete` |
| `testimonials` | list of `{provider: {name, type, affiliation, url}, text, date}` | No | — | `type` is `Person` or `Organization` |
| `identifier` | URL | No | — | Explicit DOI/handle when `url` is a plain landing page |
| `image` | path or URL | No | — | Optional thumbnail for cards |
| `date_added` | ISO 8601 date | No | — | Catalogue bookkeeping; set by the Issue-form Action |

A complete example, `_resources/usgs-metadata-wizard-tutorial.md`:

```yaml
---
title: "Writing FGDC/ISO metadata with the USGS Metadata Wizard"
description: "A 45-minute hands-on tutorial that walks through describing a geospatial dataset with the Metadata Wizard, validating the record, and exporting it for a repository submission."
url: https://example.org/metadata-wizard-tutorial
url_type: URL
identifier: https://doi.org/10.5066/EXAMPLE
resource_type: tutorial
license:
  id: CC-BY-4.0
version_date: 2025-03-14
authors:
  - name: Jane Doe
    type: Person
    orcid: https://orcid.org/0000-0000-0000-0000
  - name: U.S. Geological Survey
    type: Organization
    ror: https://ror.org/035a68863
language: en
keywords: [metadata, FGDC, ISO 19115, geospatial]
audience: [researcher, data-steward]
learning_outcomes:
  - "Create a standards-compliant metadata record for a geospatial dataset"
  - "Validate and export the record for repository deposit"
access_cost: no
expertise_level: beginner
lifecycle_stages: [process, preserve, share]
research_areas: [solid-earth, land-surface]
status: published
testimonials:
  - provider:
      name: "A. Researcher"
      type: Person
      affiliation: "Example University"
    text: "Took our group from no metadata to a validated record in one afternoon."
    date: 2025-06-02
date_added: 2025-06-10
---
Optional longer notes in Markdown: prerequisites, how the material is best used, related resources.
```

Each vocabulary file has the same shape, so one include renders any of them and one script turns any of them into an Issue-form dropdown. `_data/vocab/lifecycle_stage.yml`:

```yaml
id: lifecycle-stage
name: GeoFAIR Lifecycle Stage
description: Stage of the research data lifecycle a resource supports.
terms:
  - id: plan
    label: Plan
    definition: Designing data management before collection begins.
    same_as:
      - https://rdmkit.elixir-europe.org/planning
      - https://www.usgs.gov/data-management/plan
```

The `terms[].id` values are what resources reference; `label` and `definition` feed the page and the JSON-LD `DefinedTerm`; `same_as` (and optionally `broad_match`) carry the crosswalk to external vocabularies. Jekyll settings: `collections: resources: {output: true, permalink: /resources/:name/}` and `defaults` giving every resource `layout: resource` and `status: draft`, so a file that forgets `status` can never be published by accident.

## Controlled vocabularies: candidates and recommendation

For each facet the table lists the existing vocabularies worth considering, then the recommended approach. The pattern recommended in all four cases is the same: publish a short GeoFAIR term list as a `schema:DefinedTermSet` at a stable URL on the site, and link every term to its external equivalents with `sameAs`/`broadMatch`. That keeps the facet lists short enough to use, while staying interoperable with DataCite, LRMI and the Earth-science vocabularies. Where an external list is already the right size and has term URIs (LRMI, GCMD top level), adopting it directly is the simpler alternative and is noted.

### Lifecycle stage

| Candidate | Terms | URIs | Fit for GeoFAIR |
| --- | --- | --- | --- |
| [USGS Science Data Lifecycle Model](https://www.usgs.gov/products/data-and-tools/data-management/data-lifecycle) | Plan, Acquire, Process, Analyze, Preserve, Publish/Share; cross-cutting Describe, Manage Quality, Backup & Secure | Stable web pages per stage, no SKOS | Geoscience-native, mandated in USGS policy (SM 502.6); the cross-cutting elements map well to FAIR training topics (metadata, QA) |
| [RDMkit data life cycle (ELIXIR)](https://rdmkit.elixir-europe.org/) | Plan, Collect, Process, Analyse, Preserve, Share, Reuse | Stable page per stage, CC BY 4.0, no SKOS | Most widely reused model in RDM training (SciLifeLab, ESIP DMP guide, NFDI); includes Reuse, which FAIR training often targets |
| DCC Curation Lifecycle Model | Conceptualise, Create or Receive, Appraise and Select, Ingest, Preservation Action, Store, Access Use and Reuse, Transform | None | Archive-centric; too fine-grained for a discovery facet |
| Jisc RDM lifecycle | Plan and design; Collect and capture; Collaborate and analyse; Manage, store and preserve; Share and publish; Discover, reuse and cite | None | Similar to RDMkit; compound labels are long for facet chips |

Recommendation: a GeoFAIR set of eight terms, the seven RDMkit stages plus **Describe** (metadata and documentation, taken from the USGS cross-cutting elements) because a FAIR training hub will have many resources about metadata that fit no single stage. Each term carries `same_as` links to both the RDMkit and the USGS stage page, so the facet is readable to either community. The crosswalk: Plan→Plan; Collect→Acquire; Process→Process; Analyse→Analyze; Preserve→Preserve; Share→Publish/Share; Reuse→(no USGS stage); Describe→Describe (cross-cutting).

### Resource type

| Candidate | Terms | URIs | Fit for GeoFAIR |
| --- | --- | --- | --- |
| [LRMI Learning Resource Type](https://www.dublincore.org/specifications/lrmi/concept_schemes/learningResourceType/) (DCMI, 2022) | 10: activity plan, assessment, assessment item, educator curriculum guide, lesson plan, physical learning resource, recorded lesson, supporting document, textbook, unit plan | SKOS, `http://purl.org/dcx/lrmi-vocabs/learningResourceType/<term>` | The scheme the RDA recommendation points to; well governed and the natural `broadMatch` target. Labels are school-flavoured (lesson plan, textbook) and do not read naturally for webinars, notebooks or tools |
| [DataCite `resourceTypeGeneral`](https://datacite-metadata-schema.readthedocs.io/en/4.6/appendices/appendix-1/resourceTypeGeneral/) (4.6; 4.7 adds Poster, Presentation) | \~35 incl. Audiovisual, Book, ComputationalNotebook, InteractiveResource, Report, Software, Text, Workflow | Controlled list, no per-term URIs | Describes research outputs rather than learning genres; excellent for crosswalk and for anything that also has a DOI |
| COAR Resource Types | \~80 incl. learning object, lecture, video, software, dataset | SKOS with URIs | Repository-oriented; richer than needed for a facet |
| Bioschemas / TeSS practice | Free text: tutorial, video, e-learning module, slides, course | None | Reflects how training portals actually label things, but has no governance |

Recommendation: a GeoFAIR set of about ten training-oriented types — tutorial, online course, recorded lecture or webinar, video, slide deck, guide or handbook, template or checklist, computational notebook, interactive tool, reference material — each with `broad_match` to one LRMI concept (e.g. tutorial→activity plan, recorded lecture→recorded lesson, guide→supporting document) and `close_match` to a DataCite value (e.g. video→Audiovisual, notebook→ComputationalNotebook, slide deck→Presentation). Alternative: adopt LRMI's ten concepts unchanged, which removes maintenance but gives visitors less natural labels.

### Research area

| Candidate | Terms | URIs | Fit for GeoFAIR |
| --- | --- | --- | --- |
| [NASA GCMD Earth Science Keywords](https://vocabs.ardc.edu.au/gcmd-sciencekeywords) | \~3,000 concepts in 7 levels; top-level categories such as Atmosphere, Biosphere, Cryosphere, Land Surface, Oceans, Solid Earth, Terrestrial Hydrosphere, Human Dimensions, Climate Indicators, Paleoclimate | SKOS, UUID-based URIs, KMS REST API, governed by NASA ESDIS | The de-facto Earth-science discovery vocabulary (used by CEOS, ESIP, NOAA, Australian Antarctic Data Centre); top level alone is the right size for a facet |
| OECD Fields of Science and Technology (FOS 2007), class 1.5 Earth and related environmental sciences | Geosciences multidisciplinary; Mineralogy; Palaeontology; Geochemistry and geophysics; Physical geography; Geology; Volcanology; Environmental sciences; Meteorology and atmospheric sciences; Climatic research; Oceanography; Hydrology; Water resources | Codes, no URIs; DataCite accepts `subjectScheme="FOS"` | The scheme DataCite and the GREI repositories recommend for `subject`; good interoperability, coarse and discipline-shaped rather than system-shaped |
| USGS Thesaurus | Several thousand terms, hierarchical | SKOS available | Strong for US geoscience topics and methods; larger than a facet needs |
| ANZSRC FoR 2020, division 37 Earth Sciences | \~10 groups (geology, geophysics, hydrology, oceanography, atmospheric sciences, climate change science, physical geography, geochemistry, geoinformatics) | Codes, published as linked data by ARDC | Clean mid-size list; Australia-centric governance |
| UNESCO nomenclature, field 25 Earth and Space Sciences | \~20 disciplines | Codes only | Dated (1988) but stable |

Recommendation: adopt the GCMD Earth Science top-level categories (about 14 terms) as the GeoFAIR research-area facet, storing each term's GCMD UUID URI in `same_as` and its nearest FOS 1.5 subclass in `broad_match` so the JSON-LD can also emit a DataCite-compatible FOS subject. Add one local term, **Cross-disciplinary / Research data management**, for resources that are not domain-specific. If GeoFAIR turns out to be broader than geoscience, use FOS level-2 classes (the 42 fields) instead; the file format does not change.

### Status

| Candidate | Terms | URIs | Fit for GeoFAIR |
| --- | --- | --- | --- |
| [`schema:creativeWorkStatus`](https://schema.org/creativeWorkStatus) example terms | Incomplete, Draft, Published, Obsolete | Property exists; terms are examples only, no URIs | Matches three of your four states; the property is where the value belongs in JSON-LD |
| SPAR Publishing Status Ontology (PSO) | draft, submitted, under review, accepted, published, retracted, and others | OWL individuals with `purl.org/spar/pso/` URIs | Covers In Review precisely; scholarly-publishing flavour |
| BIBO `bibo:status` | draft, published, peer reviewed, and others | URIs | Smaller, bibliographic |
| DataCite | No status list; `IsObsoletedBy`/`Obsoletes` relation types only | — | Useful for the superseded-by link, not for status |

Recommendation: a GeoFAIR set of four terms — `draft`, `in-review`, `published`, `obsolete` — emitted through `creativeWorkStatus` as a `DefinedTerm`, with `same_as` to the PSO individual where one exists. Build rule: `draft` and `in-review` pages render (so reviewers can see them) but carry `<meta name="robots" content="noindex">` and are excluded from the search index and sitemap; `published` is the default facet selection; `obsolete` is hidden until the visitor ticks "include obsolete" and shows a banner linking to `superseded_by`.

### Smaller lists (audience, expertise level, access cost, license)

| Field | Recommendation |
| --- | --- |
| Audience | Local list of six: researcher, data steward or data manager, student, educator or trainer, repository or infrastructure staff, policy maker or funder. RDA suggests the Europass target-group list, which is employment-oriented and does not fit; emitted as `schema:EducationalAudience` with `audienceType` |
| Expertise level | beginner, intermediate, advanced (Bioschemas TrainingMaterial / TeSS convention); emitted as `educationalLevel` |
| Access cost | `no`, `yes`, `maybe` per RDA; emitted as `isAccessibleForFree` (true/false) plus a textual note when `maybe` |
| License | SPDX identifiers with a local `_data/licenses.yml` lookup for name and URL; emitted as `license` URL |

## Mapping to the RDA Minimal Metadata for Learning Resources

All 14 elements of the RDA recommendation ([Hoebelheinrich et al. 2022, DOI 10.15497/RDA00073](https://doi.org/10.15497/RDA00073), version 1.0) have a home in the front matter; six are required and the other eight are optional with defaults, as agreed. The RDA report does not grade elements as required or optional itself: all 14 are the minimal set for discovery, and the report notes that recommended and optional terms were deferred to a later extended set. Types and lengths below come from the accompanying Data Dictionary (October 2021).

| # | RDA element | RDA type, repeatable | RDA suggested vocabulary | GeoFAIR field | Required here | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Title | TEXT(1000), no | — | `title` | Yes |  |
| 2 | Abstract / Description | TEXT(2000), no | — | `description` | Yes | CI enforces the 2000-character ceiling |
| 3 | Author(s) | TEXT, yes | MARC relator terms suggested for extension | `authors[]` | No | Structured name, type, ORCID/ROR instead of a comma-separated string; rendered as a comma list for RDA-style export |
| 4 | Primary Language | TEXT(2), no | ISO 639-1 | `language` | No, default `en` | Stored as BCP 47 (ISO 639-1 codes are valid BCP 47) |
| 5 | Keyword(s) | TEXT(100), yes | Curated vocabulary recommended, none named | `keywords[]` plus vocabulary labels | No | Facet labels are appended at build time so keyword search also hits them |
| 6 | License | TEXT(100), no | NERC L08; EU Licence Authority table; "URL + human-readable name" | `license.{id,name,url}` | Yes | SPDX id resolves to both name and URL, satisfying the two-part recommendation |
| 7 | Version Date | DATE, no | ISO 8601 / RFC 3339 | `version_date` | Yes | YYYY-MM-DD |
| 8 | URL to Resource | TEXT(1000), no | URL syntax; PID preferred | `url` (+ `identifier`) | Yes |  |
| 9 | Resource URL Type | TEXT(40), no | DataCite `relatedIdentifierType` | `url_type` | No, auto-detected | Subset: URL, DOI, Handle, ARK, PURL, URN |
| 10 | Target Group (Audience) | TEXT(40), yes | Europass target groups | `audience[]` | No | Local six-term list; see vocabularies |
| 11 | Learning Resource Type | TEXT(40), no | LRMI concept scheme; CEDS | `resource_type` | Yes | GeoFAIR list with `broadMatch` to LRMI |
| 12 | Learning Outcome(s) | TEXT(1000), yes | — | `learning_outcomes[]` | No |  |
| 13 | Access Cost | TEXT(8), no | yes / no / maybe; COAR access rights as a finer option | `access_cost` | No, default `no` |  |
| 14 | Expertise (Skill) Level | TEXT(40), no | None named; examples beginner, intermediate, advanced | `expertise_level` | No |  |

GeoFAIR fields with no RDA counterpart are extensions, not conflicts: `lifecycle_stages`, `research_areas`, `status`, `superseded_by`, `testimonials`, `image`, `date_added`. In an RDA-style flat export they would be dropped or, for the two subject-like facets, folded into Keyword(s) — which is exactly what the build does for the JSON-LD `keywords` property.

Two RDA conventions are deliberately tightened. Author(s) is structured rather than a single comma-separated string, because Schema.org and DataCite both want one object per author; the layout re-joins them for display. License is an SPDX identifier rather than free text, because the RDA Data Dictionary itself records that a license vocabulary recommendation is still outstanding and asks for both a URL and a human-readable name, which SPDX supplies deterministically.

## Mapping to Schema.org and the per-page JSON-LD

Every resource page emits one `schema:LearningResource` object (the type Bioschemas uses for its TrainingMaterial profile and the one that carries the LRMI properties `learningResourceType`, `educationalLevel`, `teaches` and `audience`). Vocabulary values are `schema:DefinedTerm` objects pointing at a `schema:DefinedTermSet` published by the site, so a consumer can tell a lifecycle stage from a research area by the set it belongs to, and can follow `sameAs` to GCMD, LRMI or RDMkit. The record declares `dct:conformsTo` the Bioschemas TrainingMaterial 1.0 profile, which costs nothing and makes the pages harvestable by ELIXIR TeSS-style aggregators.

| GeoFAIR field | Schema.org property | Value shape |
| --- | --- | --- |
| page URL | `@id`, `mainEntityOfPage` | `https://<org>.github.io/<repo>/resources/<slug>/` |
| `title` | `name` | Text |
| `description` | `description` | Text |
| `url` | `url` | URL of the external material |
| `identifier` (or `url` when `url_type` is DOI/Handle/ARK) | `identifier`, `sameAs` | `PropertyValue {propertyID: "DOI", value}` and the resolvable URL |
| `resource_type` | `learningResourceType` | `DefinedTerm {name, termCode, inDefinedTermSet, sameAs[]}`; `additionalType` carries the DataCite `close_match` string |
| `license` | `license` | URL (SPDX canonical) |
| `version_date` | `dateModified` | ISO date (Schema.org has no "version date"; `dateModified` is the closest and is what Google reads) |
| `authors[]` | `author` | `Person {name, identifier: ORCID, affiliation}` or `Organization {name, identifier: ROR}` |
| `language` | `inLanguage` | BCP 47 text |
| `keywords[]` + facet labels | `keywords` | array of Text |
| `audience[]` | `audience` | `EducationalAudience {audienceType}` |
| `learning_outcomes[]` | `teaches` | array of Text |
| `access_cost` | `isAccessibleForFree` | `true` when `no`; `false` when `yes`; `false` plus a sentence in `description` when `maybe` |
| `expertise_level` | `educationalLevel` | `DefinedTerm` in the GeoFAIR expertise-level set |
| `lifecycle_stages[]` | `about` | `DefinedTerm` in the GeoFAIR lifecycle-stage set |
| `research_areas[]` | `about` | `DefinedTerm` in the GeoFAIR research-area set, `sameAs` GCMD URI |
| `status` | `creativeWorkStatus` | `DefinedTerm` in the GeoFAIR status set |
| `superseded_by` | `dct:isReplacedBy` | `@id` of the replacing resource (Schema.org has no equivalent property) |
| `testimonials[]` | `review` | `Review {reviewBody, author: Person or Organization, datePublished}` — no `reviewRating`, since testimonials are unrated |
| `image` | `image` | absolute URL |
| catalogue membership | `isPartOf` | `Collection {@id: <site>/resources/, name: "GeoFAIR Resource Hub"}` |
| profile | `dct:conformsTo` | `https://bioschemas.org/profiles/TrainingMaterial/1.0-RELEASE` |

The JSON-LD for the example resource:

```json
{
  "@context": {"@vocab": "https://schema.org/", "dct": "http://purl.org/dc/terms/"},
  "@type": "LearningResource",
  "@id": "https://<org>.github.io/<repo>/resources/usgs-metadata-wizard-tutorial/",
  "mainEntityOfPage": "https://<org>.github.io/<repo>/resources/usgs-metadata-wizard-tutorial/",
  "dct:conformsTo": {"@id": "https://bioschemas.org/profiles/TrainingMaterial/1.0-RELEASE"},
  "name": "Writing FGDC/ISO metadata with the USGS Metadata Wizard",
  "description": "A 45-minute hands-on tutorial ...",
  "url": "https://example.org/metadata-wizard-tutorial",
  "identifier": {"@type": "PropertyValue", "propertyID": "DOI", "value": "10.5066/EXAMPLE"},
  "sameAs": "https://doi.org/10.5066/EXAMPLE",
  "learningResourceType": {
    "@type": "DefinedTerm", "name": "Tutorial", "termCode": "tutorial",
    "inDefinedTermSet": "https://<org>.github.io/<repo>/vocab/resource-type/",
    "sameAs": "http://purl.org/dcx/lrmi-vocabs/learningResourceType/activityPlan"
  },
  "additionalType": "InteractiveResource",
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "dateModified": "2025-03-14",
  "author": [
    {"@type": "Person", "name": "Jane Doe", "identifier": "https://orcid.org/0000-0000-0000-0000"},
    {"@type": "Organization", "name": "U.S. Geological Survey", "identifier": "https://ror.org/035a68863"}
  ],
  "inLanguage": "en",
  "keywords": ["metadata", "FGDC", "ISO 19115", "geospatial", "Process", "Preserve", "Share", "Solid Earth", "Land Surface", "Tutorial"],
  "audience": [
    {"@type": "EducationalAudience", "audienceType": "Researcher"},
    {"@type": "EducationalAudience", "audienceType": "Data steward"}
  ],
  "teaches": ["Create a standards-compliant metadata record for a geospatial dataset", "Validate and export the record for repository deposit"],
  "isAccessibleForFree": true,
  "educationalLevel": {"@type": "DefinedTerm", "name": "Beginner", "termCode": "beginner", "inDefinedTermSet": "https://<org>.github.io/<repo>/vocab/expertise-level/"},
  "about": [
    {"@type": "DefinedTerm", "name": "Process", "termCode": "process", "inDefinedTermSet": "https://<org>.github.io/<repo>/vocab/lifecycle-stage/", "sameAs": ["https://rdmkit.elixir-europe.org/processing", "https://www.usgs.gov/data-management/process"]},
    {"@type": "DefinedTerm", "name": "Preserve", "termCode": "preserve", "inDefinedTermSet": "https://<org>.github.io/<repo>/vocab/lifecycle-stage/"},
    {"@type": "DefinedTerm", "name": "Share", "termCode": "share", "inDefinedTermSet": "https://<org>.github.io/<repo>/vocab/lifecycle-stage/"},
    {"@type": "DefinedTerm", "name": "Solid Earth", "termCode": "solid-earth", "inDefinedTermSet": "https://<org>.github.io/<repo>/vocab/research-area/", "sameAs": "https://gcmd.earthdata.nasa.gov/kms/concept/<uuid>"},
    {"@type": "DefinedTerm", "name": "Land Surface", "termCode": "land-surface", "inDefinedTermSet": "https://<org>.github.io/<repo>/vocab/research-area/"}
  ],
  "creativeWorkStatus": {"@type": "DefinedTerm", "name": "Published", "termCode": "published", "inDefinedTermSet": "https://<org>.github.io/<repo>/vocab/status/"},
  "review": [{
    "@type": "Review",
    "reviewBody": "Took our group from no metadata to a validated record in one afternoon.",
    "author": {"@type": "Person", "name": "A. Researcher", "affiliation": {"@type": "Organization", "name": "Example University"}},
    "datePublished": "2025-06-02"
  }],
  "isPartOf": {"@type": "Collection", "@id": "https://<org>.github.io/<repo>/resources/", "name": "GeoFAIR Resource Hub"}
}
```

How it is generated. A single Liquid include, `_includes/jsonld/resource.html`, takes a resource object and writes the JSON above; every string passes through `| jsonify` so quotes and newlines are escaped, arrays are emitted with `{% unless forloop.last %},{% endunless %}`, and vocabulary ids are resolved to label, definition and `same_as` with `site.data.vocab[set].terms | where: "id", term_id | first`. The resource layout wraps the include in `<script type="application/ld+json">`. The same include is called in a loop by the search page (next section), so there is exactly one template for the structured data and the two outputs cannot drift apart.

The four `DefinedTermSet` pages at `/vocab/<set>/` are generated from the same `_data/vocab/*.yml` files: each is a human-readable term list plus its own JSON-LD (`DefinedTermSet` with `hasDefinedTerm[]`, each term carrying `sameAs`), so the `inDefinedTermSet` URLs in every resource resolve to something a machine can read. A Liquid-only build can produce these as four small pages written by hand that loop over the data file, or, if a page per set is to be generated automatically, with the `jekyll-datapage-generator` plugin, which the GitHub Actions build permits.

Validation of the structured data in CI: parse every built page's JSON-LD with the `jsonld` npm package (catches malformed JSON and bad `@context`), then check each object against the Bioschemas TrainingMaterial SHACL shapes with `pyshacl`, and against a small GeoFAIR SHACL shape that asserts the `DefinedTermSet` URLs are the site's own. The Google Rich Results test and the Schema.org validator remain manual spot checks.

## Faceted search page

The search page at `/resources/` embeds one `<script type="application/ld+json" id="resource-index">` containing a `schema:ItemList` whose `itemListElement` entries are the same `LearningResource` objects the individual pages emit, produced by looping the same include over `site.resources | where: "status", "published"` (plus `obsolete`, flagged). A dependency-free script of roughly 200 lines parses that block, derives the facets, and filters in the browser; nothing is fetched at runtime and the page is valid, crawlable structured data on its own. The same list is also written to `/resources.jsonld` so that anyone can harvest the catalogue without scraping, which is the "JSON-LD data element constructed from the individual resources" you described, made available in two places from one template.

| Facet | Source in the JSON-LD | Selection logic | Default |
| --- | --- | --- | --- |
| Lifecycle stage | `about[]` where `inDefinedTermSet` ends in `/lifecycle-stage/` | Multi-select, OR within the facet | none |
| Resource type | `learningResourceType.termCode` | Multi-select, OR within the facet | none |
| Research area | `about[]` where `inDefinedTermSet` ends in `/research-area/` | Multi-select, OR within the facet | none |
| Status | `creativeWorkStatus.termCode` | Single toggle: "include obsolete" | published only |
| Expertise level | `educationalLevel.termCode` | Multi-select | none |
| Audience | `audience[].audienceType` | Multi-select | none |
| Free of charge | `isAccessibleForFree` | Checkbox | off |
| Keyword search | `name`, `description`, `keywords[]`, `teaches[]`, `author[].name` | Case-folded token match, all tokens must hit | empty |

Facets combine with AND across facets and OR within a facet, which is the behaviour visitors expect from library catalogues. Each facet shows a live count of matching resources for every term, computed from the currently filtered set with that facet's own selection ignored, so a term never shows a zero count that the visitor could not reach. Term labels and definitions come from the `DefinedTerm` objects themselves, so the vocabulary files remain the single source. Expertise level, audience and free-of-charge are included because they are present in every record and cost nothing; they can be dropped from the UI with one line if the panel is too busy.

Behaviour and state:

1. On load the script reads the ItemList, builds an in-memory array with lower-cased search text per item, and renders the facet panel from the terms present (ordered as in the vocabulary file, not alphabetically, so lifecycle stages appear in lifecycle order).
2. Every selection is written to the URL query string (`?stage=plan,collect&type=tutorial&q=metadata`), so a filtered view can be bookmarked or shared, and the page restores it on load.
3. Results render as cards: title linking to the resource page, type and level chips, a two-line description, lifecycle and research-area chips, and an external-link icon to the material. Obsolete items, when shown, carry an "Obsolete" badge.
4. Keyword matching is a plain token match. If the catalogue grows past a few hundred items or fuzzy matching is wanted, swap the matcher for MiniSearch (about 7 kB, no dependencies) without changing the data source; ItemsJS is the alternative if facet counting should also be delegated to a library.
5. The page emits `aria-live` updates for the result count, every control is a real `<input>` with a `<label>`, and the panel is keyboard-operable; no framework is used.

No-JavaScript fallback: the page body includes a `<noscript>` block, generated by Liquid at build time, that lists every published resource grouped under lifecycle-stage headings with the same card content and links. Search engines and text browsers therefore see the complete catalogue, and the JSON-LD above it still describes every item.

Performance: at roughly 2 kB of JSON-LD per resource, a 300-resource catalogue embeds about 600 kB before compression and 60–80 kB gzipped, which GitHub Pages serves compressed. Past roughly 1,000 resources the index should move out of the page into `/resources.jsonld` fetched on load, keeping only a lighter `ItemList` of names and URLs inline; the script needs a one-line change for this, so the design does not need to decide it now.

## Repository, build pipeline and contributor workflow

The repository is a plain Jekyll 4 site with no theme gem and no third-party Jekyll plugins; everything specific to the hub is Liquid, YAML data, one JavaScript file and two GitHub Actions workflows. The build runs in GitHub Actions rather than the Pages default builder, which lifts the Jekyll 3.x and plugin-whitelist limits and, more importantly, lets a validation job fail the build before anything is deployed.

```text
.
├── _config.yml                 # collections, defaults, url/baseurl, vocab paths
├── _resources/                 # one Markdown file per resource
├── _data/
│   ├── vocab/                  # lifecycle_stage.yml, resource_type.yml, research_area.yml,
│   │                           # status.yml, audience.yml, expertise_level.yml
│   └── licenses.yml            # SPDX id -> name, url
├── _layouts/
│   ├── default.html
│   ├── resource.html           # page + JSON-LD + noindex when not published
│   └── vocab.html              # DefinedTermSet page + JSON-LD
├── _includes/
│   ├── jsonld/resource.html    # the single JSON-LD template
│   ├── resource-card.html      # card used by search results and noscript list
│   └── facet-panel.html
├── resources/index.html        # faceted search page (ItemList JSON-LD + noscript list)
├── resources.jsonld            # same ItemList as a standalone file
├── vocab/                      # one page per vocabulary, or generated
├── assets/js/facets.js         # client-side faceting, no dependencies
├── schema/
│   ├── resource.schema.json    # JSON Schema for front matter
│   └── geofair-shapes.ttl      # SHACL shape for the emitted JSON-LD
├── scripts/
│   ├── validate_resources.py   # front matter vs schema + vocab ids + URL reachability
│   ├── validate_jsonld.py      # parse built pages, pyshacl against shapes
│   ├── issue_to_resource.py    # Issue form body -> Markdown file
│   └── build_issue_form.py     # vocab yml -> .github/ISSUE_TEMPLATE/new-resource.yml
├── .github/
│   ├── ISSUE_TEMPLATE/new-resource.yml
│   ├── workflows/pages.yml     # validate -> build -> deploy on push to main
│   └── workflows/issue-to-pr.yml
└── CONTRIBUTING.md, README.md, LICENSE
```

GitHub Pages constraints that shape the design: the site is static, so faceting is client-side; the Pages default builder would pin Jekyll 3.10 and a plugin whitelist, so the Actions route is used (`actions/jekyll-build-pages` or a plain `bundle exec jekyll build` plus `actions/upload-pages-artifact` and `actions/deploy-pages`); project sites live under `/<repo>/`, so every absolute URL in the JSON-LD is built from `site.url | append: site.baseurl`; and there is no server-side redirect, so an obsolete resource keeps its page and points forward with `superseded_by` rather than redirecting.

The pipeline: a contributor submits the Issue form; a workflow converts the issue to a resource file and opens a PR; CI validates it; a maintainer reviews, sets `status: published` and merges; the Pages workflow builds, validates the emitted JSON-LD, and deploys. Maintainers may also open PRs directly, entering the same flow at the second step.

&#91;embedded content: contribution and deployment pipeline · 7 steps, 1 gate\]

A failed check loops back to the contributor on the PR; only a merged, re-validated build is deployed.

Validation steps run on every PR and again before deploy:

| Check | Tool | Fails the build when |
| --- | --- | --- |
| Front matter against `schema/resource.schema.json` | `jsonschema` (Python) via `validate_resources.py` | Missing required field, wrong type, description over 2000 characters, bad date |
| Vocabulary ids exist | same script, reads `_data/vocab/*.yml` | Any `lifecycle_stages`, `research_areas`, `resource_type`, `status`, `audience` value not in its file |
| Slug and filename | same script | Filename not kebab-case, duplicate titles |
| External `url` resolves | `requests` HEAD with retry, allow-list for known bot-blocking hosts | 4xx/5xx after retries (warning only on PRs from forks, error on main) |
| License id known | `_data/licenses.yml` lookup | Unknown SPDX id |
| Built JSON-LD parses and conforms | `jsonld` (npm) + `pyshacl` with Bioschemas TrainingMaterial shapes and `geofair-shapes.ttl` | Any resource page or the ItemList fails |
| Issue form in sync with vocabularies | `build_issue_form.py --check` | Dropdown options differ from the vocab files |
| Jekyll build | `jekyll build --strict_front_matter` | Liquid error or malformed front matter |

Contributor workflow in detail. The Issue form (`new-resource.yml`) has text inputs for title, URL, description, authors, learning outcomes, keywords and testimonials, and dropdowns for resource type, license, language, expertise level, access cost, plus multi-select checkboxes for lifecycle stages, research areas and audience. The dropdown and checkbox options are generated from the vocabulary files by `build_issue_form.py`, so a new term is added in one place and CI refuses a stale form. On submission, `issue-to-pr.yml` parses the issue body (the Issue-form body is deterministic Markdown, so a small parser or the `github-issue-parser` action suffices), writes `_resources/<slug>.md` with `status: in-review` and `date_added` set to today, opens a PR that references the issue, and comments on the issue with the PR link. CODEOWNERS assigns the repository owner as reviewer; merging closes the issue. Editing an existing resource follows the same path through an "Update a resource" Issue form that asks for the slug, or by direct PR.

## Phased implementation plan

Six phases, each ending at a gate that can be checked objectively; a working, deployed site exists from the end of Phase 1, and every later phase adds to it without reworking the schema. Effort figures are estimates for one developer and exclude content writing.

&#91;embedded content: implementation roadmap · 6 phases, 6 gates\]

Phases run left to right then wrap; the diamond at each phase's edge is its gate, and the last gate is launch.

| Phase | Deliverables | Gate (acceptance criteria) | Estimated effort |
| --- | --- | --- | --- |
| 0 – Decisions | Vocabulary choice per facet from the candidates section; repository name and organisation; audience and expertise-level lists confirmed; six `_data/vocab/*.yml` files drafted with definitions and `same_as` links | You approve the six vocabulary files; `url` and `baseurl` known | 1–2 days, mostly review time |
| 1 – Skeleton site | Repository, `_config.yml`, `_resources` collection, layouts, the JSON-LD include, vocabulary pages with `DefinedTermSet` JSON-LD, five sample resources, Pages workflow (build + deploy) | Site live on GitHub Pages; each sample page passes the Schema.org validator and the Google Rich Results test with no errors; `inDefinedTermSet` URLs resolve | 3–4 days |
| 2 – Validation | `resource.schema.json`, `validate_resources.py`, `validate_jsonld.py` with Bioschemas and GeoFAIR SHACL shapes, CI on pull requests, `--strict_front_matter` | A PR with a missing required field, an unknown vocabulary id, or a 2001-character description is rejected by CI with a readable message; a valid PR passes | 2–3 days |
| 3 – Search page | `/resources/` with ItemList JSON-LD, `facets.js`, facet counts, URL state, keyword search, obsolete toggle, `<noscript>` list, `/resources.jsonld` | AND-across/OR-within behaviour verified on the samples; full catalogue visible with JavaScript disabled; keyboard-only operation and screen-reader announcement of result counts; Lighthouse accessibility score 95 or above | 3–4 days |
| 4 – Contributor workflow | `build_issue_form.py` and the generated Issue form, `issue-to-pr.yml`, update-a-resource form, CONTRIBUTING.md, CODEOWNERS, PR template | A resource submitted through the Issue form appears as a PR within minutes, passes CI, and is live after merge with `status: published`; a stale Issue form fails CI | 2–3 days |
| 5 – Content and launch | Initial resource set entered and reviewed, theme and typography polish, README, a `CITATION.cff` for the hub, announcement text | Agreed initial set published; no CI warnings; vocabulary pages and search page linked from the home page | Depends on the number of resources; 1–2 days of engineering |

Sequencing notes. Phase 2 can start in parallel with Phase 1 once the schema table in this document is accepted, because the JSON Schema is derived from that table alone. Phase 3 depends on Phase 1's JSON-LD include being stable, since the search page reuses it unchanged. Phase 4 depends on Phase 2, because the Issue-form parser and the validator share the same field definitions. Nothing in Phases 3–5 changes a resource file, so content entry can begin as soon as Phase 2 is complete.

## Sources

- Hoebelheinrich, N. J. et al. (2022). *Recommendations for a minimal metadata set to aid harmonised discovery of learning resources*, v1.0. Research Data Alliance. [DOI 10.15497/RDA00073](https://doi.org/10.15497/RDA00073); [report PDF](https://archive.rd-alliance.org/system/files/Recommondations_MinimalMD4LearningResources.pdf); [Data Dictionary, Oct 2021](https://archive.rd-alliance.org/system/files/Copy%20of%20Report_Snapshot_DataDictionary.pdf)
- [LRMI Learning Resource Type Concept Scheme](https://www.dublincore.org/specifications/lrmi/concept_schemes/learningResourceType/), DCMI, issued 2022-04-05; [Turtle](https://www.dublincore.org/vocabs/learningResourceType.ttl)
- [DataCite Metadata Schema 4.6, Appendix 1: resourceTypeGeneral](https://datacite-metadata-schema.readthedocs.io/en/4.6/appendices/appendix-1/resourceTypeGeneral/) and [release history](https://schema.datacite.org/versions.html) (4.7 adds Poster and Presentation)
- [Bioschemas TrainingMaterial profile 1.0-RELEASE](https://bioschemas.org/profiles/TrainingMaterial/1.0-RELEASE) and the [Bioschemas training tutorial](https://bioschemas.org/tutorials/community/training) showing `LearningResource` + `dct:conformsTo` markup
- [Schema.org `creativeWorkStatus`](https://schema.org/creativeWorkStatus); [LearningResource](https://schema.org/LearningResource); [DefinedTerm](https://schema.org/DefinedTerm); [Review](https://schema.org/Review)
- [USGS Science Data Lifecycle Model](https://www.usgs.gov/products/data-and-tools/data-management/data-lifecycle) and [USGS Survey Manual 502.6](https://www.usgs.gov/about/organization/science-support/survey-manual/5026-fundamental-science-practices-scientific-data)
- [RDMkit data life cycle (ELIXIR)](https://rdmkit.elixir-europe.org/), as reused by [SciLifeLab](https://data-guidelines.scilifelab.se/data-life-cycle/) and the [ESIP DMP guide](https://esipfed.github.io/esipDMP/sections/introduction/data_lifecycle.html)
- [NASA GCMD Science Keywords](https://vocabs.ardc.edu.au/gcmd-sciencekeywords) (ARDC SKOS mirror, v18.1); [GCMD Keywords overview](https://commons.esipfed.org/node/9568)
- [OECD Revised Fields of Science and Technology (FOS 2007)](https://edutechwiki.unige.ch/en/Fields_of_science_and_technology_classifications); [GREI metadata recommendations on DataCite 4.6](https://zenodo.org/records/16953589) recommending FOS for subjects
- [Jisc RDM lifecycle](https://jisc.ac.uk/guides/rdm-toolkit/software)

Retrieved 2026-11-06. The vocabulary sizes and version numbers quoted above are as published on those pages at that date.
