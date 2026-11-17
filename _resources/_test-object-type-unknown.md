---
# VALIDATION FIXTURE — object type given as the DataCite label instead of the id.
# Skipped from the build (filename starts with '_'); checked by scripts/test_validation.py.
# EXPECT: 'Dataset' is not a term in _data/vocab/object_type.yml
local_id: test-object-type-unknown
slug: object-type-unknown
title: "Validation fixture: object type given as the DataCite label instead of the id"
description: "A deliberately non-conforming resource used by scripts/test_validation.py to check that the validator catches one specific problem. It is never built because its filename starts with an underscore."
resource_url: https://example.org/test
url_type: URL
resource_type: guide
object_types: [Dataset]
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
