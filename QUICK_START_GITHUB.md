# Quick Start: Make CloudOpti Globally Accessible

This guide will help you publish CloudOpti to GitHub and make it installable from anywhere.

## 🚀 Quick Steps

### 1. Prepare the Code

Run the preparation script with your GitHub username:

```bash
python prepare_for_github.py YOUR_GITHUB_USERNAME
```

This will update all URLs in the codebase with your GitHub username.

**Example:**
```bash
python prepare_for_github.py johndoe
```

### 2. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `cloudopti`
3. Description: "AWS Cost Monitoring and Optimization Tool"
4. Choose **Public**
5. **DO NOT** check any initialization options
6. Click "Create repository"

### 3. Push Code to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: CloudOpti V2.0.0"

# Add your GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/cloudopti.git

# Push to GitHub
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

### 4. Test Installation from GitHub

Once pushed, test that it works:

```bash
# Uninstall local version (if installed)
pip uninstall cloudopti -y

# Install from GitHub
pip install git+https://github.com/YOUR_USERNAME/cloudopti.git

# Test the command
opti --help
```

### 5. (Optional) Publish to PyPI

For global installation via `pip install cloudopti`:

#### Option A: Manual Publishing

1. Create PyPI account: https://pypi.org/account/register/
2. Generate API token: https://pypi.org/manage/account/token/
3. Build and upload:
   ```bash
   pip install build twine
   python -m build
   twine upload dist/*
   ```
   - Username: `__token__`
   - Password: Your API token

#### Option B: Automated via GitHub Actions

1. Go to GitHub repository → Settings → Secrets → Actions
2. Add secret: `PYPI_API_TOKEN` with your PyPI API token
3. Create a GitHub Release (this triggers automatic publishing)

## ✅ Verification

After publishing, anyone can install:

```bash
# From PyPI (once published)
pip install cloudopti

# From GitHub (always available)
pip install git+https://github.com/YOUR_USERNAME/cloudopti.git
```

Then run:
```bash
opti aws
```

## 📋 Files Created

The following files have been created to help with distribution:

- `setup.py` - Package configuration for PyPI
- `pyproject.toml` - Modern Python packaging config
- `MANIFEST.in` - Files to include in distribution
- `LICENSE` - MIT License
- `.github/workflows/` - Automated testing and publishing
- `GITHUB_SETUP.md` - Detailed GitHub setup guide
- `PUBLISH.md` - PyPI publishing guide
- `INSTALL.md` - Installation instructions
- `CONTRIBUTING.md` - Contribution guidelines

## 🎯 What Users Will See

Once published, users can:

1. **Install globally:**
   ```bash
   pip install cloudopti
   ```

2. **Run from anywhere:**
   ```bash
   opti aws
   ```

3. **Get help:**
   ```bash
   opti --help
   ```

## 🔧 Troubleshooting

### Git push fails
- Check authentication: `git config --global user.name` and `git config --global user.email`
- Verify remote: `git remote -v`

### Installation fails
- Ensure Python 3.8+ is installed
- Try: `pip install --upgrade pip` first

### Command not found
- Check PATH includes pip's bin directory
- Linux/Mac: `export PATH=$PATH:~/.local/bin`
- Windows: Add Python Scripts to PATH

## 📚 Next Steps

1. ✅ Run preparation script
2. ✅ Create GitHub repository
3. ✅ Push code to GitHub
4. ✅ Test installation from GitHub
5. ⬜ (Optional) Publish to PyPI
6. ⬜ Share with others!

## 💡 Tips

- **Test first**: Always test installation from GitHub before publishing to PyPI
- **Version management**: Update version in `setup.py` and `pyproject.toml` for new releases
- **Documentation**: Keep README.md updated with latest features
- **Releases**: Use GitHub Releases for version tracking

## 🆘 Need Help?

- Check `GITHUB_SETUP.md` for detailed GitHub setup
- Check `PUBLISH.md` for PyPI publishing details
- Check `INSTALL.md` for installation troubleshooting
- Open an issue on GitHub if you encounter problems

