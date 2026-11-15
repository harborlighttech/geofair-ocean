---
# SAMPLE ENTRY — replace or delete before launch. The URL is a placeholder.
title: "Working with Argo float profiles in Python"
description: "A two-hour, hands-on tutorial that downloads Argo temperature and salinity profiles, reads the netCDF files with xarray, applies the quality-control flags correctly, and plots a section. Assumes basic Python; no prior oceanography is needed."
resource_url: https://example.org/tutorials/argo-python
url_type: URL
resource_type: tutorial
license:
  id: CC-BY-4.0
version_date: 2025-02-10
authors:
  - name: "A. Example"
    type: Person
    orcid: https://orcid.org/0000-0000-0000-0001
    affiliation: "Example Oceanographic Institute"
language: en
keywords: [Argo, netCDF, xarray, quality control, profiles]
audience: [researcher, student]
learning_outcomes:
  - "Locate and download Argo profiles for a region and period"
  - "Interpret Argo quality-control flags before analysis"
  - "Plot a temperature–salinity section with xarray and matplotlib"
access_cost: "no"
expertise_level: beginner
object_types: [interactive-resource, computational-notebook, dataset]
lifecycle_stages: [collect, process, analyse, reuse]
research_areas: [ocean-temperature, salinity-density, ocean-observing-systems]
status: published
testimonials:
  - provider:
      name: "B. Reader"
      type: Person
      affiliation: "Example University"
    text: "The QC-flag section alone saved my group a week of confused plots."
    date: 2025-05-14
date_added: 2025-06-01
---
Prerequisites: Python 3.10 or later with `xarray`, `netCDF4` and `matplotlib` installed. The tutorial's data download step needs about 200 MB of disk space.
