---
layout: vocab
title: Digital object type
vocab: object_type
permalink: /vocab/object-type/
---
Ids follow the [DataCite Metadata Schema 4.7 `resourceTypeGeneral`](https://datacite-metadata-schema.readthedocs.io/en/4.7/appendices/appendix-1/resourceTypeGeneral/) controlled list. Each term records its [COAR Resource Types 3.2](https://vocabularies.coar-repositories.org/resource_types/) concept URI where one exists (marked *broad* or *close* when the match is not exact) and the DCMI Type class that DataCite suggests as the Dublin Core mapping. A resource's object types are emitted in its JSON-LD as `schema:additionalType`: the COAR URI when present, otherwise the DCMI URI, otherwise the DataCite value as text.
