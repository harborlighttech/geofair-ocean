---
# VALIDATION FIXTURE — url_type outside the allowed list.
# Skipped from the build (filename starts with '_'); checked by scripts/test_validation.py.
# EXPECT: 'Link' is not one of
local_id: test-url-type-invalid
slug: url-type-invalid
title: "Validation fixture: url_type outside the allowed list"
description: "A deliberately non-conforming resource used by scripts/test_validation.py to check that the validator catches one specific problem. It is never built because its filename starts with an underscore."
resource_url: https://example.org/test
url_type: Link
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
