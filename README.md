📘 PM Catalog: Playbooks, Templates & Learning Paths
Welcome to my public catalog — a curated library of free and premium resources for product managers.
This repo powers the site at:
👉 https://amycmitchell14-create.github.io/PM-catalog/
All free content is hosted here on GitHub Pages. Premium content is delivered via Substack.


📚 What’s Inside
This catalog includes:
	• 🟢 Free PM resources
Quick-starts, templates, checklists, and learning paths.
	• 🔒 Premium playbooks
Strategy guides and deep dives for paid subscribers.
	• 📄 A living index
Automatically generated from catalog.yml using GitHub Actions.
	• ❓ A public FAQ
Answers to common questions about access, licensing, and how to use the catalog.


🔗 Quick Links
	• 📘 View the full catalog:
GitHub Pages site
	• ❓ Read the FAQ:
faq.md
	• 📰 Subscribe on Substack:
https://your-substack-url
	• 📂 Browse free content:
public/


🛠 How This Repo Works
This repo uses:
	• catalog.yml as the source of truth
	• scripts/catalog_to_md.py to generate index.md
	• GitHub Actions to automate publishing
	• GitHub Pages for free content
	• Google Drive links for premium content
	• Substack for gated distribution and subscriber management

📜 License
All free content is licensed under:
Creative Commons BY‑NC 4.0
→ Free to use, not for commercial use.

👋 Maintainer
Amy Mitchell
Product Manager & Systems Thinker
(email optional)


🖐 Logo & Branding
Your logo is attached to this repo and may be used for visual identity across GitHub Pages and Substack.
If you’d like help integrating it into your homepage or catalog header, I can walk you through the Markdown or CSS options.


# catalog
newsletter content catalog

## catalog.yml

This repository uses `catalog.yml` at the project root to declare metadata about the content in `content/`.

How to update:


Example with extended fields:

```yaml
items:
	- id: pm-urgency-checklist
		title: "PM Urgency Checklist"
		filename: "PM urgency checklist.pdf"
		file: "content/PM urgency checklist.pdf"
		path: "content/PM urgency checklist.pdf"
		type: "Quick Start"
		version: "1.0"
		description: "Steps to handle sudden priority shifts"
		tags: ["PM steps", "PM leadership"]
		access: "paid"
		status: "current"
```

### Tools: render catalog to Markdown

There's a small helper script at `scripts/catalog_to_md.py` which reads `catalog.yml` and prints a Markdown summary of the catalog. It depends on PyYAML — install the dependency with:

```powershell
pip install -r requirements.txt
```

Example usage (run from the repo root):

```powershell
python scripts/catalog_to_md.py -c catalog.yml       # print to stdout
python scripts/catalog_to_md.py -c catalog.yml -o README-catalog.md   # write to a file
```

The output includes the catalog name, description, maintainer, and one Markdown section per item showing type, version, status, access, description, tags and file/path.

## Schema & CI

This project includes a small schema validator and a GitHub Actions workflow that will run on pushes and PRs to `main`.

- Minimum schema checks (enforced by `scripts/validate_catalog.py`):
	- top-level `name` exists
	- `items` is present and is a list
	- each item must contain: `id`, `title` (or `filename`), `file`/`path`/`filename`, `type`, `version`, `description`, `tags` (list), `access`, and `status`

- The workflow at `.github/workflows/generate-catalog.yml`:
	- installs dependencies (`requirements.txt`)
	- parses `catalog.yml` to confirm valid YAML
	- runs `scripts/validate_catalog.py` (schema checks)
	- runs `scripts/catalog_to_md.py` to render `README-catalog.md`
	- commits `README-catalog.md` back to the branch if it changed (using `GITHUB_TOKEN`)

If a schema validation fails, the workflow fails and the generated README will not be committed.
