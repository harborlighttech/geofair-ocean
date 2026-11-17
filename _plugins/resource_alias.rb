# frozen_string_literal: true
#
# Generates a redirect page at /resources/<local_id>/<slug>/ for every resource,
# so that a readable URL resolves to the canonical page /resources/<local_id>/.
# The slug is the resource's `slug` front-matter value, or its title slugified.
#
# This is a local plugin: it runs in the GitHub Actions build (and `jekyll build`
# locally) but not under the GitHub Pages default builder, which passes --safe.
module GeoFAIR
  class ResourceAliasGenerator < Jekyll::Generator
    safe true
    priority :low

    def generate(site)
      collection = site.collections["resources"]
      return unless collection

      root = "#{site.config['url']}#{site.config['baseurl']}"
      collection.docs.each do |doc|
        local_id = doc.data["local_id"].to_s
        next if local_id.empty?

        slug = doc.data["slug"].to_s
        slug = Jekyll::Utils.slugify(doc.data["title"].to_s) if slug.empty?
        next if slug.empty?

        canonical_rel = "#{site.config['baseurl']}#{doc.url}"
        canonical_abs = "#{root}#{doc.url}"
        page = Jekyll::PageWithoutAFile.new(site, site.source, File.join("resources", local_id, slug), "index.html")
        page.data["layout"] = nil
        page.data["sitemap"] = false
        page.data["title"] = doc.data["title"]
        page.content = <<~HTML
          <!DOCTYPE html>
          <html lang="en">
          <head>
            <meta charset="utf-8">
            <title>#{CGI.escapeHTML(doc.data['title'].to_s)}</title>
            <link rel="canonical" href="#{canonical_abs}">
            <meta name="robots" content="noindex">
            <meta http-equiv="refresh" content="0; url=#{canonical_rel}">
            <script>location.replace(#{canonical_rel.to_json});</script>
          </head>
          <body>
            <p>Redirecting to <a href="#{canonical_rel}">#{canonical_abs}</a>.</p>
          </body>
          </html>
        HTML
        site.pages << page
      end
    end
  end
end
