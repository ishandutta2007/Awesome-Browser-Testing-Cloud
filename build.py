import os
import re
import urllib.request
import json
import subprocess

README_PATH = "README.md"

def run_git(msg):
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", msg], check=True)

def read_readme():
    with open(README_PATH, "r", encoding="utf-8") as f:
        return f.read()

def write_readme(content):
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

def step1_saas():
    content = read_readme()
    # Find the SaaS table
    table_pattern = re.compile(r"(\| Platform \| Description \| Pricing & Free Tier Limits \|.*?)(?=\n\n|\Z)", re.DOTALL)
    match = table_pattern.search(content)
    if not match: return
    table_text = match.group(1)
    lines = table_text.strip().split('\n')
    header = lines[0]
    separator = lines[1]
    rows = lines[2:]

    # Add valuation column to header and separator
    new_header = header + " Valuation/Size |"
    new_separator = separator + "---|"
    
    # Valuations mapping (approximated)
    valuations = {
        "BrowserStack": (4000, "$4B"),
        "Sauce Labs": (1000, "$1B+"),
        "SmartBear": (1000, "$1B+"),
        "Perfecto": (200, "$200M"),
        "HeadSpin": (300, "$300M"),
        "LambdaTest": (100, "$100M+"),
        "Kobiton": (30, "$30M+"),
        "BitBar": (1000, "$1B+ (SmartBear)"),
        "TestingBot": (1, "Startup"),
        "TestGrid": (1, "Startup"),
        "CrossBrowserTesting": (1000, "$1B+ (SmartBear)"),
    }
    
    new_rows = []
    for row in rows:
        val_sort = 0
        val_str = "Unknown"
        for k, v in valuations.items():
            if k in row:
                val_sort = v[0]
                val_str = v[1]
                break
        new_rows.append((val_sort, row + f" {val_str} |"))
    
    new_rows.sort(key=lambda x: x[0], reverse=True)
    
    new_table = "\n".join([new_header, new_separator] + [x[1] for x in new_rows])
    content = content.replace(table_text, new_table)
    write_readme(content)
    run_git("Added company size and sorted the SaaS based on that")

def step2_opensource():
    content = read_readme()
    
    # Find the Open source list
    lines = content.split('\n')
    in_os = False
    os_lines = []
    os_start = -1
    os_end = -1
    for i, line in enumerate(lines):
        if "### Dedicated Browser Testing & Automation Tools" in line:
            in_os = True
            os_start = i + 2
            continue
        if in_os and line.startswith("###"):
            os_end = i
            in_os = False
            break
        if in_os:
            if line.strip().startswith("- **["):
                # it's an OS entry
                pass

    # Wait, the structure is:
    # - **[Name](repo_url)**
    #   Description
    
    os_block = lines[os_start:os_end]
    entries = []
    current_entry = []
    for line in os_block:
        if line.strip().startswith("- **["):
            if current_entry:
                entries.append(current_entry)
            current_entry = [line]
        elif current_entry and line.strip():
            current_entry.append(line)
    if current_entry:
        entries.append(current_entry)
        
    parsed_entries = []
    for entry in entries:
        title_line = entry[0]
        match = re.search(r"- \*\*\[(.*?)\]\((.*?)\)\*\*", title_line)
        if match:
            name, url = match.groups()
            repo_path = url.replace("https://github.com/", "").strip("/")
            
            # Fetch stars
            stars = 0
            try:
                req = urllib.request.Request(f"https://api.github.com/repos/{repo_path}", headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode())
                    stars = data.get("stargazers_count", 0)
            except Exception as e:
                print(f"Failed to fetch stars for {repo_path}: {e}")
                pass
            
            badge_url = f"https://img.shields.io/github/stars/{repo_path}?style=social&color=white"
            badge_md = f"[![Stars]({badge_url})]({url}/stargazers)"
            
            new_title = f"- **[{name}]({url})** {badge_md}"
            entry[0] = new_title
            parsed_entries.append((stars, entry))
        else:
            parsed_entries.append((-1, entry))
            
    parsed_entries.sort(key=lambda x: x[0], reverse=True)
    
    new_os_block = []
    for _, entry in parsed_entries:
        new_os_block.extend(entry)
        new_os_block.append("")
        
    lines = lines[:os_start] + new_os_block + lines[os_end:]
    content = "\n".join(lines)
    write_readme(content)
    run_git("Added github stars and sorted the opensource based on that")

def step3_banner():
    svg_content = '''<svg width="800" height="200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4facfe;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#00f2fe;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#grad)" rx="15" ry="15"/>
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="Arial" font-size="40" font-weight="bold" fill="white">
    Awesome Browser Testing Cloud
    <animate attributeName="opacity" values="0.5;1;0.5" dur="2s" repeatCount="indefinite" />
  </text>
</svg>'''
    with open("assets/banner.svg", "w") as f:
        f.write(svg_content)
        
    content = read_readme()
    banner_md = "![Banner](assets/banner.svg)\n"
    content = banner_md + content
    write_readme(content)
    run_git("added banner")

def step4_emojis():
    content = read_readme()
    content = content.replace("## Top Browser Testing Cloud Ecosystem", "## 🌐 Top Browser Testing Cloud Ecosystem")
    content = content.replace("## Table of Contents", "## 📑 Table of Contents")
    content = content.replace("## SaaS/Hosted Platforms", "## ☁️ SaaS/Hosted Platforms")
    content = content.replace("## Open-Source GitHub Projects", "## 💻 Open-Source GitHub Projects")
    content = content.replace("## How to Contribute", "## 🤝 How to Contribute")
    content = content.replace("## Disclaimer", "## ⚠️ Disclaimer")
    write_readme(content)
    run_git("added emojis")

def step5_seo():
    content = read_readme()
    seo_text = """
<meta name="description" content="A curated list of the best browser testing clouds, SaaS platforms, and open-source GitHub projects for cross-browser testing and automation.">
<meta name="keywords" content="browser testing, cross-browser testing, automated testing, selenium grid, playwright, device cloud">
"""
    content = content.replace("# Awesome-Browser-Testing-Cloud", "# Awesome-Browser-Testing-Cloud\n" + seo_text)
    write_readme(content)
    run_git("seo optimised")

def step6_badges_left():
    content = read_readme()
    left_badges = '<a href="https://github.com/ishandutta2007/Awesome-Awesome-Awesome"><img src="https://img.shields.io/badge/Awesome-%E2%9C%94-blueviolet?style=flat-square&logo=github" alt="Awesome"/></a><a href="https://discord.gg/jc4xtF58Ve"><img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord" /></a>'
    
    # Insert right below the SEO meta tags
    # Let's create a badges section
    content = content.replace(seo_text, seo_text + "\n<div id='badges'>\n" + left_badges + "\n</div>\n")
    write_readme(content)
    run_git("badges to left added")

def step7_badges_right():
    content = read_readme()
    right_badge = '<a href="https://github.com/ishandutta2007"><img alt="GitHub followers" src="https://img.shields.io/github/followers/ishandutta2007?label=Follow" /></a>'
    content = content.replace("\n</div>\n", " " + right_badge + "\n</div>\n")
    write_readme(content)
    run_git("badges to right added")

def step8_star_history():
    content = read_readme()
    star_history = """
## ⭐️ Star History
<div align="center">
<a href="https://www.star-history.com/?repos=ishandutta2007%2FAwesome-Browser-Testing-Cloud&type=date&legend=bottom-right">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=ishandutta2007/Awesome-Browser-Testing-Cloud&type=date&theme=dark&legend=bottom-right" />
<source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=ishandutta2007/Awesome-Browser-Testing-Cloud&type=date&legend=bottom-right" />
<img alt="Star History Chart" src="https://api.star-history.com/chart?repos=ishandutta2007/Awesome-Browser-Testing-Cloud&type=date&legend=bottom-right" />
</picture>
</a>
</div>
"""
    content += "\n" + star_history
    write_readme(content)
    run_git("star history added")
    
def step9_fix_chartrepos():
    content = read_readme()
    content = content.replace("chartrepos", "chart?repos")
    write_readme(content)
    run_git("fixed star plot")

def step10_fix_awesome_link():
    content = read_readme()
    content = content.replace("https://github.com/sindresorhus/awesome", "https://github.com/ishandutta2007/Awesome-Awesome-Awesome")
    write_readme(content)
    run_git("invalid awesome link fixed")

def main():
    print("Step 1")
    step1_saas()
    print("Step 2")
    step2_opensource()
    print("Step 3")
    step3_banner()
    print("Step 4")
    step4_emojis()
    print("Step 5")
    step5_seo()
    print("Step 6")
    step6_badges_left()
    print("Step 7")
    step7_badges_right()
    print("Step 8")
    step8_star_history()
    print("Step 9")
    step9_fix_chartrepos()
    print("Step 10")
    step10_fix_awesome_link()

if __name__ == "__main__":
    main()
