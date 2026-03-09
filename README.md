## Features

- Analyze a local repository or a GitHub repository URL
- Count total files and directories
- Show language breakdown by file extension
- Show largest files
- Detect duplicate filenames
- Flag possible secret-like strings
- Export results as JSON
- Ignore common junk/build directories

## Installation

> First install git in your system 

```bash
git clone https://github.com/ExVoider/repo-analyzer.git
cd repo-analyzer
```

## Usage

```
python repo_analyzer.py .
python repo_analyzer.py ~/projects/exif-cli
python repo_analyzer.py https://github.com/ExVoider/exif-cli.git
python repo_analyzer.py https://github.com/ExVoider/exif-cli
python repo_analyzer.py . --json
```

## Example output 

```
Repository : /home/user/project
Total Files: 128
Total Dirs : 21
Total Size : 3.4 MB

Language Breakdown
------------------
Python          44
JavaScript      18
Markdown        5
JSON            4

Largest Files
-------------
420.2 KB   /home/user/project/data/sample.json
210.5 KB   /home/user/project/build/output.js

Duplicate Filenames
-------------------
index.js                  3
README.md                 2

Possible Secrets
----------------
/home/user/project/.env:1 -> BOT_TOKEN=...
/home/user/project/config.py:12 -> api_key = "..."
```
