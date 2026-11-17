---
# VALIDATION FIXTURE — ORCID given without the https://orcid.org/ prefix.
# Skipped from the build (filename starts with '_'); checked by scripts/test_validation.py.
# EXPECT: does not match
local_id: test-orcid-malformed
slug: orcid-malformed
title: "Validation fixture: ORCID given without the https://orcid.org/ prefix"
description: "A deliberately non-conforming resource used by scripts/test_validation.py to check that the validator catches one specific problem. It is never built because its filename starts with an underscore."
resource_url: https://example.org/test
url_type: URL
resource_type: guide
object_types: [text]
license:
  id: CC-BY-4.0
version_date: 2026-01-01
language: en
authors:
  - name: "A. Person"
    type: Person
    orcid: 0000-0002-1825-0097
access_cost: "no"
expertise_level: beginner
lifecycle_stages: [plan]
research_areas: [research-data-management]
status: draft
---
