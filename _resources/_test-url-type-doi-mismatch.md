---
# VALIDATION FIXTURE — DOI URL declared as url_type URL (warning).
# Skipped from the build (filename starts with '_'); checked by scripts/test_validation.py.
# EXPECT: resource_url is a DOI; url_type should be DOI
local_id: test-url-type-doi-mismatch
slug: url-type-doi-mismatch
title: "Validation fixture: DOI URL declared as url_type URL (warning)"
description: "A deliberately non-conforming resource used by scripts/test_validation.py to check that the validator catches one specific problem. It is never built because its filename starts with an underscore."
resource_url: https://doi.org/10.5281/zenodo.0000000
url_type: URL
resource_type: guide
object_types: [text]
license:
  id: CC-BY-4.0
version_date: 2026-01-01
language: en
access_cost: "no"
expertise_level: beginner
lifecycle_stages: [plan]
research_areas: [research-data-management]
status: draft
---
