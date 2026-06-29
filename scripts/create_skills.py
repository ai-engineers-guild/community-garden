import sys
from pathlib import Path

sys.path.insert(0, str(Path("src").absolute()))
from community_garden.skills.templates import BUILTIN_SKILLS

base_dir = Path(".agents/skills")
base_dir.mkdir(parents=True, exist_ok=True)

descriptions = {
    "semantic_metrics": "Evaluate semantic metrics like belonging, safety, self_sustainability, rule_alignment.",
    "role_analysis": "Analyze actor roles such as steward, expert, bridge, bartender, noise_generator, risk_actor.",
    "risk_analysis": "Identify behavioral risks like newcomer churn, overload, emotional dumping, norm erosion.",
    "tribe_analysis": "Discover candidate groups/tribes, their leaders, values, symbols, and conflicts.",
    "admin_mirror": "Analyze admin actions, omissions, over-moderation, under-moderation, and rule effectiveness.",
    "recommendations": "Produce concrete DevRel actions based on metrics, risks, and findings.",
    "comprehensive_report": "Generate a colossal, deeply analytical Markdown report based on community data.",
    "community_garden": "Core workflow skill for analyzing community exports and maintaining recurring reports.",
}

for key, content in BUILTIN_SKILLS.items():
    skill_name = key.split("/")[0]
    if skill_name.endswith(".md") or skill_name.endswith(".yml"):
        skill_name = skill_name.replace(".md", "").replace(".yml", "")

    skill_dir = base_dir / skill_name
    skill_dir.mkdir(exist_ok=True)

    desc = descriptions.get(skill_name, f"Skill for {skill_name}")

    # We will write everything into SKILL.md for the agent
    skill_md = skill_dir / "SKILL.md"

    frontmatter = f"---\nname: {skill_name}\ndescription: {desc}\n---\n\n"

    # if it already exists, we append or overwrite. Let's overwrite.
    # But wait, some keys map to the same skill_dir (e.g. if we had multiple).
    # Currently each is unique: semantic_metrics/registry.yml, role_analysis/roles.yml, etc.
    with open(skill_md, "w", encoding="utf-8") as f:
        f.write(frontmatter + content)

print("Skills created successfully in .agents/skills/")
