---
# VALIDATION FIXTURE — filename does not match the local identifier.
# Skipped from the build (filename starts with '_'); checked by scripts/test_validation.py.
# EXPECT: filename must be 'other-id_<slug>.md' (or 'other-id.md')
local_id: other-id
slug: local-id-filename-mismatch
title: "Validation fixture: filename does not match the local identifier"
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
---
