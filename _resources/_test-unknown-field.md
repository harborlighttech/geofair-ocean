---
# VALIDATION FIXTURE — a field that is not in the schema.
# Skipped from the build (filename starts with '_'); checked by scripts/test_validation.py.
# EXPECT: Additional properties are not allowed ('rating' was unexpected)
local_id: test-unknown-field
slug: unknown-field
title: "Validation fixture: a field that is not in the schema"
description: "A deliberately non-conforming resource used by scripts/test_validation.py to check that the validator catches one specific problem. It is never built because its filename starts with an underscore."
resource_url: https://example.org/test
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
rating: 5
---
