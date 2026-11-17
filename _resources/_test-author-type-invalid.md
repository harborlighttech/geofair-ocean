---
# VALIDATION FIXTURE — author type outside Person / Organization.
# Skipped from the build (filename starts with '_'); checked by scripts/test_validation.py.
# EXPECT: 'Group' is not one of
local_id: test-author-type-invalid
slug: author-type-invalid
title: "Validation fixture: author type outside Person / Organization"
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
  - name: "A. Group"
    type: Group
access_cost: "no"
expertise_level: beginner
lifecycle_stages: [plan]
research_areas: [research-data-management]
status: draft
---
