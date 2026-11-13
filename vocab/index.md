---
title: Vocabularies
permalink: /vocab/
---
# Controlled vocabularies

The facets on the [resources page]({{ '/resources/' | relative_url }}) use these term lists. Each is published as a Schema.org `DefinedTermSet` with a stable URL, and every term links to its equivalents in external vocabularies where they exist.

| Vocabulary | Field | Values | Terms |
| --- | --- | --- | --- |
{% for v in site.data.vocab -%}
| [{{ v[1].name }}]({{ '/vocab/' | append: v[1].id | append: '/' | relative_url }}) | `{{ v[1].field }}` | {% if v[1].cardinality == "many" %}one or more{% else %}one{% endif %} | {{ v[1].terms | size }} |
{% endfor %}

To propose a new term, open an issue in the [repository]({{ site.github_repo }}/issues). Terms are edited in `_data/vocab/*.yml`; the search page, the resource pages, the Issue form and the validator all read from those files.
