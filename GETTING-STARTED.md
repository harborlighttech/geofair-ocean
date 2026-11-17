# Getting started: publishing a GeoFAIR Resource Hub on GitHub Pages

This walks a domain owner from a fresh copy of the repository to a live site. It takes about fifteen minutes. The examples use `harborlighttech/geofair-ocean`; substitute your own organisation and repository name.

## 1. Get the files into GitHub with the hidden files included

The repository must contain the `.github/` folder (workflows, Issue forms, CODEOWNERS) and `.gitignore`. These are hidden files, and the Finder/Explorer drag-and-drop upload skips them silently. Check the repository's file list on GitHub: if `.github` is not there, the site will never build.

- **macOS Finder:** press `⌘ + Shift + .` to show hidden files, then select them along with everything else before dragging into GitHub's *Upload files* page.
- **Command line (recommended):**

  ```bash
  cd geofair-ocean
  git init -b main
  git add -A            # includes dot-files
  git commit -m "Initial import"
  git remote add origin https://github.com/<org>/<repo>.git
  git push -u origin main
  ```

## 2. Fill in the site configuration

Open `_config.yml` and replace every `TODO` in the first block.

| Key | Value for a project site at `https://<org>.github.io/<repo>/` |
| --- | --- |
| `title`, `domain`, `tagline`, `description` | Your domain's wording |
| `organization`, `organization_url` | Who runs the hub |
| `url` | `https://<org>.github.io` (no trailing slash) |
| `baseurl` | `/<repo>` (leading slash, no trailing slash) |
| `github_repo` | `https://github.com/<org>/<repo>` |
| `footer_links` | The repo URL and `https://github.com/<org>/<repo>/issues/new?template=new-resource.yml` |
| `theme_colors` | Your palette; every value becomes a CSS variable (defaults are the AGU brand colours) |
| `fonts` | Display and body font stacks and the Google Fonts URL that loads them; `google_fonts_url: ""` for system fonts only |
| `logo`, `logo_alt`, `logo_height` | Optional logo shown before the site title in the header: a path under the site or an `https://` URL; empty shows nothing |

For an organisation site (`https://<org>.github.io/`) or a custom domain, set `baseurl: ""`.

Then edit `.github/CODEOWNERS` and replace `@example-owner` with the GitHub handle(s) that should review every pull request.

`url` matters more than it looks: it is used to build the `@id` of every resource in the JSON-LD. A wrong value still builds, but the structured data will point at a host that does not exist.

## 3. Set the Pages source to GitHub Actions

1. On GitHub, open the repository and click **Settings** (far right of the tab bar).
2. In the left sidebar, under *Code and automation*, click **Pages**.
3. Under *Build and deployment*, open the **Source** dropdown and choose **GitHub Actions**. Do not choose *Deploy from a branch*.
4. GitHub may suggest a starter Jekyll workflow. Ignore it; the repository already has `.github/workflows/pages.yml`.

There is no save button; the choice takes effect immediately.

## 4. Allow Actions to write and open pull requests

The Issue-form workflow turns a submitted form into a pull request, which needs write permission.

1. **Settings → Actions → General**.
2. Scroll to *Workflow permissions*.
3. Select **Read and write permissions**.
4. Tick **Allow GitHub Actions to create and approve pull requests**.
5. Click **Save**.

## 5. Trigger the first build and watch it

Commit and push the `_config.yml` and CODEOWNERS changes from step 2. Every push to `main` runs the workflow **Validate, build and deploy**, which you can follow under the **Actions** tab. It has three jobs:

| Job | What it does | Typical failure |
| --- | --- | --- |
| `validate` | Checks every file in `_resources/` against the schema and the vocabularies; checks the Issue forms match the vocabulary files | A resource with a missing required field or an unknown vocabulary id; forms not regenerated after a vocabulary edit |
| `build` | Runs Jekyll, then checks every JSON-LD block in the output | A Liquid or YAML error in a resource or layout |
| `deploy` | Publishes `_site/` to GitHub Pages | Pages source not set to *GitHub Actions* (step 3) |

If nothing has run (for example you set the Pages source after your last push), open the workflow under *Actions*, click **Run workflow**, and run it on `main`.

The site is live at `https://<org>.github.io/<repo>/` when `deploy` finishes, usually one to two minutes after the push.

## 6. If a job fails

Click the red job, expand the failing step, and read the last lines of the log. The validator prints one line per problem with the file name and field. Fix the file, push, and the workflow runs again.

## 7. Replace the sample content

The six files in `_resources/` whose names start with `sample-` are placeholders with `example.org` links. Delete them or overwrite them with real resources, then push. The field reference is in `CONTRIBUTING.md`.

Review `_data/vocab/research_area.yml` for your domain and fill in the `same_as` links to external vocabulary terms. After any change to a file in `_data/vocab/`, regenerate the Issue forms and commit the result, or the `validate` job will fail:

```bash
pip install -r requirements.txt
python scripts/build_issue_form.py
```

## 8. Test the contributor path

Open **Issues → New issue → Suggest a resource**, fill in the form and submit. Within a minute or two a pull request titled *New resource: …* should appear, with the new file under `_resources/` and `status: in-review`. Review it, change `status` to `published`, merge, and the resource appears on the site after the next deploy.

## Checklist

- [ ] `.github/` folder and `.gitignore` present in the repository
- [ ] `_config.yml`: `url`, `baseurl`, `github_repo`, `footer_links` set; no `TODO` left
- [ ] `.github/CODEOWNERS` names a real reviewer
- [ ] Settings → Pages → Source = GitHub Actions
- [ ] Settings → Actions → General → Read and write permissions, and PR creation allowed
- [ ] First workflow run green; site opens at `https://<org>.github.io/<repo>/`
- [ ] Sample resources replaced
- [ ] Issue form tested end to end

## Working documents in the repository

Jekyll copies any Markdown file that has no front matter straight into the published site as raw text. Keep planning documents and notes out of the public site by putting them in a `docs/` folder and adding `docs` to the `exclude:` list in `_config.yml` (this file, `README.md` and `CONTRIBUTING.md` are already excluded).
