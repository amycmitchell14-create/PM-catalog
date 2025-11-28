import yaml

# Load catalog.yml
with open("catalog.yml", "r") as f:
    catalog = yaml.safe_load(f)

# Define section headers
sections = {
    "slide-deck": "🎤 Slide Decks",
    "learning-guide": "📖 Learning Guides",
    "quick-start": "📝 Quick Starts"
}

# Define badge logic
def badge(item):
    from datetime import datetime
    updated = datetime.strptime(item["updated"], "%Y-%m-%d")
    days = (datetime.now() - updated).days
    if item.get("status") == "new" and days <= 14:
        return "🆕"
    elif item.get("status") == "updated" and days <= 60:
        return "🔄"
    return ""

# Build Markdown
def build_catalog(access_type):
    lines = [f"# 📚 {access_type.capitalize()} Content Catalog\n"]
    lines.append("This catalog is auto-generated from `catalog.yml`\n")

    for section, header in sections.items():
        lines.append(f"## {header}")
        for item in catalog["content"]:
            if item["type"] == section and item["access"] == access_type:
                tag = badge(item)
                lines.append(f"- **{item['title']} ({item['version']}) {tag}**  ")
                lines.append(f"  [View File]({item['file']})  ")
                lines.append(f"  *Updated {item['updated']} — {item['description']}*\n")
    return "\n".join(lines)

# Write output files
with open("public/free.md", "w") as f:
    f.write(build_catalog("free"))

with open("public/paid.md", "w") as f:
    f.write(build_catalog("paid"))
