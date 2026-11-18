---
title: About
main_class: page-prose
permalink: /about/
---
# About this hub

The {{ site.title }} is a curated catalogue of learning and training resources for managing, sharing and reusing {{ site.domain | downcase }} science data. It is maintained by {{ site.organization }} and built from a public GitHub repository, so anyone can suggest a resource or an edit.

## What is catalogued

External learning resources: tutorials, courses, recorded lectures, guides, templates, notebooks and tools. The catalogue describes them and links out; it does not host them.

## How resources are described

Each entry follows the [RDA Minimal Metadata for Learning Resources](https://doi.org/10.15497/RDA00073) recommendation (title, description, authors, language, keywords, licence, version date, URL and URL type, audience, resource type, learning outcomes, access cost, expertise level) and adds four {{ site.organization }} facets: lifecycle stage, resource type, research area and status. The controlled vocabularies behind those facets are published under [Vocabularies]({{ '/vocab/' | relative_url }}) with mappings to LRMI, DataCite, NASA GCMD and the RDMkit and USGS lifecycle models.

Every resource page carries a [Schema.org LearningResource](https://schema.org/LearningResource) description in JSON-LD, conforming to the [Bioschemas TrainingMaterial](https://bioschemas.org/profiles/TrainingMaterial/1.0-RELEASE) profile, and the whole catalogue is available as one file at [`/resources.jsonld`]({{ '/resources.jsonld' | relative_url }}).

## Reuse

Catalogue metadata is licensed CC BY 4.0. Each resource keeps its own licence, shown on its page.

{% if site.analytics.google.measurement_id and site.analytics.google.measurement_id != "" -%}
## Usage statistics

This site uses Google Analytics 4 to count page views, resource views, click-throughs to resources and search terms, so that maintainers can see which resources are reached and used. No advertising or demographic features are enabled, IP addresses are not stored, and no account or personal details are collected. Browsers that send a Global Privacy Control or Do Not Track signal are not measured at all. You can also [opt out]({{ '/about/?ga-optout=1' | relative_url }}) in this browser at any time (and [opt back in]({{ '/about/?ga-optout=0' | relative_url }})).
{%- endif %}
