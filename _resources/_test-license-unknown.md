---
# VALIDATION FIXTURE — licence id not in _data/licenses.yml.
# Skipped from the build (filename starts with '_'); checked by scripts/test_validation.py.
# EXPECT: license.id 'CC-BY' is not in _data/licenses.yml
local_id: test-license-unknown
slug: license-unknown
title: "Validation fixture: licence id not in _data/licenses.yml"
description: "A deliberately non-conforming resource used by scripts/test_validation.py to check that the validator catches one specific problem. It is never built because its filename starts with an underscore."
resource_url: https://example.org/test
url_type: URL
resource_type: guide
object_types: [text]
license:
  id: CC-BY
version_date: 2026-01-01
language: en
access_cost: "no"
expertise_level: beginner
lifecycle_stages: [plan]
research_areas: [research-data-management]
status: draft
---
