# frozen_string_literal: true
#
# Every resource is built twice:
#   /resources/<local_id>/          the canonical page (Jekyll's own output for the document)
#   /resources/<local_id>/<slug>/   a full copy of the same page, generated here, whose
#                                   <link rel="canonical"> and JSON-LD @id point at the
#                                   canonical URL. Site links use this readable form.
# The slug is the document's `slug` (set from the filename by the hook above, or
# explicitly in front matter), or its title slugified.
# A misspelled slug is handled by 404.html, which redirects to the canonical URL.
#
# This is a local plugin: it runs in the GitHub Actions build and in `jekyll build`,
# but not under the GitHub Pages default builder, which passes --safe.
# Resource files are named <local_id>_<slug>.md. The canonical URL comes from the
# front matter's local_id, not the filename, and the slug comes from the filename
# (after "<local_id>_") unless the front matter sets `slug` explicitly.
Jekyll::Hooks.register :documents, :post_read do |doc|
  next unless doc.collection && doc.collection.label == "resources"

  local_id = doc.data["local_id"].to_s
  next if local_id.empty?

  doc.data["permalink"] = "/resources/#{local_id}/"
  if doc.data["slug"].to_s.empty?
    stem = File.basename(doc.relative_path, ".*")
    doc.data["slug"] = stem.sub(/\A#{Regexp.escape(local_id)}_/, "") if stem.start_with?("#{local_id}_")
  end
end

module GeoFAIR
  class ResourceAliasGenerator < Jekyll::Generator
    safe true
    priority :low

    def generate(site)
      collection = site.collections["resources"]
      return unless collection

      collection.docs.each do |doc|
        local_id = doc.data["local_id"].to_s
        next if local_id.empty?

        slug = doc.data["slug"].to_s
        slug = Jekyll::Utils.slugify(doc.data["title"].to_s) if slug.empty?
        next if slug.empty?

        page = Jekyll::PageWithoutAFile.new(site, site.source, File.join("resources", local_id, slug), "index.md")
        page.data = doc.data.dup
        page.data["canonical_path"] = doc.url          # used by layouts and the JSON-LD include
        page.data["source_path"] = doc.relative_path   # used by the "Suggest an edit" link
        page.data["is_alias"] = true
        page.content = doc.content
        site.pages << page
      end
    end
  end
end
