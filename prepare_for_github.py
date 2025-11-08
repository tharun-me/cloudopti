#!/usr/bin/env python3
"""
Script to prepare CloudOpti for GitHub and PyPI distribution.
Updates placeholder URLs with your GitHub username.
"""

import re
import sys
from pathlib import Path

def update_file(file_path, old_pattern, new_pattern):
    """Update file with new pattern"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Updated {file_path}")
            return True
        else:
            print(f"[WARN] Pattern not found in {file_path}")
            return False
    except Exception as e:
        print(f"[ERROR] Error updating {file_path}: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python prepare_for_github.py <your_github_username>")
        print("Example: python prepare_for_github.py johndoe")
        sys.exit(1)
    
    github_username = sys.argv[1]
    github_url = f"https://github.com/{github_username}/cloudopti"
    
    print("Preparing CloudOpti for GitHub...")
    print(f"GitHub Username: {github_username}")
    print(f"GitHub URL: {github_url}\n")
    
    files_to_update = {
        'setup.py': [
            ('https://github.com/yourusername/cloudopti', github_url),
            ('cloudopti@example.com', 'cloudopti@example.com'),  # Update this manually
        ],
        'pyproject.toml': [
            ('https://github.com/yourusername/cloudopti', github_url),
            ('cloudopti@example.com', 'cloudopti@example.com'),  # Update this manually
        ],
        'README.md': [
            ('https://github.com/yourusername/cloudopti.git', f'{github_url}.git'),
        ],
        'INSTALL.md': [
            ('https://github.com/yourusername/cloudopti.git', f'{github_url}.git'),
        ],
        'PUBLISH.md': [
            ('https://github.com/yourusername/cloudopti', github_url),
        ],
        'CONTRIBUTING.md': [
            ('https://github.com/yourusername/cloudopti.git', f'{github_url}.git'),
        ],
        'GITHUB_SETUP.md': [
            ('YOUR_USERNAME', github_username),
            ('https://github.com/YOUR_USERNAME/cloudopti.git', f'{github_url}.git'),
        ],
    }
    
    updated_count = 0
    for file_path, replacements in files_to_update.items():
        if Path(file_path).exists():
            for old, new in replacements:
                if update_file(file_path, old, new):
                    updated_count += 1
        else:
            print(f"[WARN] File not found: {file_path}")
    
    print(f"\n[SUCCESS] Updated {updated_count} files")
    print("\nNext steps:")
    print("1. Review the updated files")
    print("2. Update email addresses in setup.py and pyproject.toml if needed")
    print("3. Initialize git: git init")
    print("4. Add files: git add .")
    print("5. Commit: git commit -m 'Initial commit'")
    print("6. Add remote: git remote add origin " + github_url + ".git")
    print("7. Push: git push -u origin main")
    print("\nSee GITHUB_SETUP.md for detailed instructions")

if __name__ == '__main__':
    main()

