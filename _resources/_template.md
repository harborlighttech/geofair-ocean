---
# TEMPLATE — copy this file to _resources/<local_id>_<slug>.md and fill it in.
# Files whose name starts with "_" (like this one) are never built.
# Field reference: CONTRIBUTING.md. Vocabulary ids: _data/vocab/*.yml or /vocab/ on the site.
local_id: template                       # letters, digits, . - _ ; unique; becomes /resources/<local_id>/
# slug: example-resource-title          # optional; by default the slug is the filename part after "<local_id>_"
title: "Example resource title"
description: "Two to four sentences: what the resource covers, how long it takes, what the learner needs first. Between 40 and 2000 characters."
resource_url: https://example.org/resource          # landing page or DOI/handle URL
url_type: URL                            # URL | DOI | Handle | ARK | PURL | URN (inferred if omitted)
# identifier: https://doi.org/10.xxxx/xxxxx         # when resource_url is a plain landing page
resource_type: tutorial                  # one id from resource_type.yml
object_types: [text]                     # one or more ids from object_type.yml (DataCite types)
license:
  id: CC-BY-4.0                          # SPDX id from _data/licenses.yml
version_date: 2026-01-01                 # date of the current version of the resource
authors:
  - name: "Person Name"
    type: Person                         # Person | Organization
    orcid: https://orcid.org/0000-0000-0000-0000
    affiliation: "Organisation"
language: en
keywords: [keyword one, keyword two]
audience: [researcher]                   # ids from audience.yml
learning_outcomes:
  - "What a learner can do after using the resource"
access_cost: "no"                        # "no" | "yes" | "maybe" — keep the quotes
expertise_level: beginner                # beginner | intermediate | advanced
lifecycle_stages: [plan]                 # one or more ids from lifecycle_stage.yml
research_areas: [research-data-management]   # one or more ids from research_area.yml
status: draft                            # draft | in-review | published | obsolete
# superseded_by: other-local-id          # when status is obsolete
# testimonials:
#   - provider: {name: "Person Name", type: Person, affiliation: "Organisation"}
#     text: "A sentence or two from someone who used the resource."
#     date: 2026-01-01
date_added: 2026-01-01
---
Optional longer notes in Markdown: prerequisites, how the material is best used, related resources.
