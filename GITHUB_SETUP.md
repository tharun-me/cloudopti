# GitHub Setup Guide for CloudOpti

This guide will help you set up CloudOpti on GitHub and make it globally accessible.

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `cloudopti`
3. Description: "AWS Cost Monitoring and Optimization Tool - Similar to Prowler but for cost optimization"
4. Choose **Public** (or Private if you prefer)
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 2: Initialize Git Repository (if not already done)

If you haven't initialized git yet, run these commands:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: CloudOpti V2.0.0"

# Add your GitHub repository as remote
git remote add origin https://github.com/testuser/cloudopti.git

# Push to GitHub
git branch -M main
git push -u origin main
```

Replace `testuser` with your actual GitHub username.

## Step 3: Update Repository URLs

Before pushing, update these files with your GitHub username:

1. **setup.py** - Line 11: Update `url` field
2. **pyproject.toml** - Update all `project.urls` entries
3. **README.md** - Update GitHub URLs in installation section
4. **INSTALL.md** - Update GitHub URLs
5. **PUBLISH.md** - Update GitHub URLs

Search for `yourusername` and replace with your actual GitHub username.

## Step 4: Push to GitHub

```bash
git add .
git commit -m "Setup for GitHub and PyPI distribution"
git push origin main
```

## Step 5: Test Installation from GitHub

Once pushed, test that others can install it:

```bash
# Uninstall local version
pip uninstall cloudopti -y

# Install from GitHub
pip install git+https://github.com/testuser/cloudopti.git

# Test the command
opti --help
```

## Step 6: Publish to PyPI (Optional but Recommended)

### Option A: Manual Publishing

1. Create PyPI account: https://pypi.org/account/register/
2. Generate API token: https://pypi.org/manage/account/token/
3. Build package:
   ```bash
   pip install build twine
   python -m build
   ```
4. Upload to PyPI:
   ```bash
   twine upload dist/*
   ```
   - Username: `__token__`
   - Password: Your API token

### Option B: Automated Publishing via GitHub Actions

1. Go to your GitHub repository
2. Settings → Secrets → Actions
3. Add new secret:
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI API token
4. Create a GitHub Release:
   - Go to Releases → Create a new release
   - Tag: `v2.0.0`
   - Title: `CloudOpti v2.0.0`
   - Description: Initial release
   - Click "Publish release"
5. GitHub Actions will automatically publish to PyPI

## Step 7: Verify Global Installation

After publishing to PyPI, anyone can install:

```bash
pip install cloudopti
opti aws
```

## Quick Reference

### For Users (Installation)

```bash
# From PyPI (once published)
pip install cloudopti

# From GitHub (always available)
pip install git+https://github.com/testuser/cloudopti.git

# From source
git clone https://github.com/testuser/cloudopti.git
cd cloudopti
pip install -e .
```

### For Developers (Contributing)

```bash
git clone https://github.com/testuser/cloudopti.git
cd cloudopti
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

## Troubleshooting

### Git push fails

- Check if you have write access to the repository
- Verify remote URL: `git remote -v`
- Ensure you're authenticated: `git config --global user.name` and `git config --global user.email`

### Installation fails

- Ensure Python 3.8+ is installed
- Check internet connection
- Try: `pip install --upgrade pip` first

### Command not found after installation

- Check PATH includes pip's bin directory
- On Linux/Mac: `export PATH=$PATH:~/.local/bin`
- On Windows: Add Python Scripts to PATH

## Next Steps

1. ✅ Create GitHub repository
2. ✅ Push code to GitHub
3. ✅ Update URLs in files
4. ✅ Test installation from GitHub
5. ⬜ Publish to PyPI (optional)
6. ⬜ Share with others!

## Support

If you encounter any issues:
1. Check the README.md for common solutions
2. Open an issue on GitHub
3. Check existing issues for similar problems

