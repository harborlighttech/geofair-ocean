---
# VALIDATION FIXTURE — superseded_by pointing at a non-existent local identifier.
# Skipped from the build (filename starts with '_'); checked by scripts/test_validation.py.
# EXPECT: superseded_by 'no-such-id' is not the local_id of any resource
local_id: test-superseded-by-unknown
slug: superseded-by-unknown
title: "Validation fixture: superseded_by pointing at a non-existent local identifier"
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
status: obsolete
superseded_by: no-such-id
---
