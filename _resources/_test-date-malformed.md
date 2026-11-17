---
# VALIDATION FIXTURE — version_date not in YYYY-MM-DD form.
# Skipped from the build (filename starts with '_'); checked by scripts/test_validation.py.
# EXPECT: does not match
local_id: test-date-malformed
slug: date-malformed
title: "Validation fixture: version_date not in YYYY-MM-DD form"
description: "A deliberately non-conforming resource used by scripts/test_validation.py to check that the validator catches one specific problem. It is never built because its filename starts with an underscore."
resource_url: https://example.org/test
url_type: URL
resource_type: guide
object_types: [text]
license:
  id: CC-BY-4.0
version_date: "14 March 2026"
language: en
access_cost: "no"
expertise_level: beginner
lifecycle_stages: [plan]
research_areas: [research-data-management]
status: draft
---
