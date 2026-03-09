import os
import sys
import json
from collections import Counter

IGNORED_DIRS = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    ".idea",
    ".vscode",
    "target",
    ".next",
}

EXTENSION_LANG_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "JavaScript",
    ".tsx": "TypeScript",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".go": "Go",
    ".c": "C",
    ".h": "C",
    ".cpp": "C++",
    ".hpp": "C++",
    ".java": "Java",
    ".php": "PHP",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".json": "JSON",
    ".md": "Markdown",
    ".sh": "Shell",
    ".zig": "Zig",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".toml": "TOML",
    ".xml": "XML",
}

SECRET_PATTERNS = [
    "api_key",
    "apikey",
    "secret_key",
    "access_key",
    "auth_token",
    "bot_token",
    "password",
    "private_key",
    "bearer ",
    "sk-",
    "ghp_",
]


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{num_bytes} B"


def detect_language(filename: str) -> str:
    _, ext = os.path.splitext(filename.lower())
    return EXTENSION_LANG_MAP.get(ext, "Other")


def should_skip_dir(dirname: str) -> bool:
    return dirname in IGNORED_DIRS


def scan_repo(root: str):
    total_files = 0
    total_dirs = 0
    total_bytes = 0
    language_counter = Counter()
    largest_files = []
    duplicate_names = Counter()
    possible_secrets = []

    for current_root, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if not should_skip_dir(d)]
        total_dirs += len(dirs)

        for name in files:
            path = os.path.join(current_root, name)

            try:
                stat = os.stat(path)
            except OSError:
                continue

            size = stat.st_size
            total_files += 1
            total_bytes += size

            language = detect_language(name)
            language_counter[language] += 1
            duplicate_names[name] += 1

            largest_files.append((size, path))

            check_possible_secret(path, possible_secrets)

    largest_files.sort(reverse=True, key=lambda x: x[0])
    top_largest = largest_files[:10]

    duplicates = [(name, count) for name, count in duplicate_names.items() if count > 1]
    duplicates.sort(key=lambda x: x[1], reverse=True)

    return {
        "root": os.path.abspath(root),
        "total_files": total_files,
        "total_dirs": total_dirs,
        "total_size_bytes": total_bytes,
        "language_breakdown": dict(language_counter.most_common()),
        "largest_files": [
            {"path": path, "size_bytes": size, "size_human": human_size(size)}
            for size, path in top_largest
        ],
        "duplicate_filenames": duplicates[:10],
        "possible_secrets": possible_secrets[:20],
    }


def check_possible_secret(path: str, results: list):
    try:
        if os.path.getsize(path) > 2_000_000:
            return

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, start=1):
                lowered = line.lower()
                if any(p in lowered for p in SECRET_PATTERNS):
                    snippet = line.strip()
                    if len(snippet) > 120:
                        snippet = snippet[:117] + "..."
                    results.append(
                        {
                            "path": path,
                            "line": i,
                            "snippet": snippet,
                        }
                    )
    except Exception:
        return


def print_report(report: dict):
    print(f"Repository : {report['root']}")
    print(f"Total Files: {report['total_files']}")
    print(f"Total Dirs : {report['total_dirs']}")
    print(f"Total Size : {human_size(report['total_size_bytes'])}")
    print()

    print("Language Breakdown")
    print("------------------")
    if report["language_breakdown"]:
        for lang, count in report["language_breakdown"].items():
            print(f"{lang:<15} {count}")
    else:
        print("No files found.")
    print()

    print("Largest Files")
    print("-------------")
    if report["largest_files"]:
        for item in report["largest_files"]:
            print(f"{item['size_human']:<10} {item['path']}")
    else:
        print("None")
    print()

    print("Duplicate Filenames")
    print("-------------------")
    if report["duplicate_filenames"]:
        for name, count in report["duplicate_filenames"]:
            print(f"{name:<25} {count}")
    else:
        print("None")
    print()

    print("Possible Secrets")
    print("----------------")
    if report["possible_secrets"]:
        for item in report["possible_secrets"]:
            print(f"{item['path']}:{item['line']} -> {item['snippet']}")
    else:
        print("None found.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python repo_analyzer.py <repo_path> [--json]")
        sys.exit(1)

    root = sys.argv[1]
    as_json = len(sys.argv) >= 3 and sys.argv[2] == "--json"

    if not os.path.isdir(root):
        print(f"Error: directory not found -> {root}")
        sys.exit(1)

    report = scan_repo(root)

    if as_json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)


if __name__ == "__main__":
    main()
