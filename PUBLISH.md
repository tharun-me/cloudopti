# Publishing CloudOpti to PyPI

This guide explains how to publish CloudOpti to PyPI so it can be installed globally with `pip install cloudopti`.

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/account/register/
2. **TestPyPI Account** (optional, for testing): https://test.pypi.org/account/register/
3. **API Token**: Generate an API token at https://pypi.org/manage/account/token/

## Step 1: Update Package Information

Before publishing, update these files with your information:

1. **setup.py**: Update `author_email` and `url` fields
2. **pyproject.toml**: Update `authors` and `project.urls`
3. **README.md**: Update GitHub URLs

## Step 2: Build the Package

```bash
# Install build tools
pip install build twine

# Build the package
python -m build
```

This creates:
- `dist/cloudopti-2.0.0.tar.gz` (source distribution)
- `dist/cloudopti-2.0.0-py3-none-any.whl` (wheel distribution)

## Step 3: Test on TestPyPI (Recommended)

First, test the package on TestPyPI:

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ cloudopti
```

## Step 4: Publish to PyPI

Once tested, publish to the real PyPI:

```bash
# Upload to PyPI
twine upload dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your PyPI API token

## Step 5: Verify Installation

After publishing, verify the package can be installed:

```bash
# Uninstall local version first
pip uninstall cloudopti

# Install from PyPI
pip install cloudopti

# Test the command
opti --help
```

## Using GitHub Actions (Automated Publishing)

The repository includes a GitHub Actions workflow (`.github/workflows/publish.yml`) that automatically publishes to PyPI when you create a release.

### Setup:

1. Go to your GitHub repository
2. Navigate to Settings → Secrets → Actions
3. Add a new secret named `PYPI_API_TOKEN` with your PyPI API token

### Publishing:

1. Create a new release on GitHub
2. The workflow will automatically build and publish to PyPI

## Version Management

To release a new version:

1. Update version in:
   - `setup.py` (version field)
   - `pyproject.toml` (version field)
   - `cloudopti/__init__.py` (__version__)

2. Commit and tag:
   ```bash
   git add .
   git commit -m "Release version 2.0.0"
   git tag v2.0.0
   git push origin main --tags
   ```

3. Create a GitHub release or manually publish

## Troubleshooting

### "Package already exists" error

- Version number must be unique
- Increment version number in setup.py and pyproject.toml

### "Invalid distribution" error

- Ensure all required files are included (check MANIFEST.in)
- Verify setup.py is correct

### Authentication errors

- Use API token, not password
- Username should be `__token__`
- Token should have "Upload packages" scope

## Alternative: Install from GitHub

Users can also install directly from GitHub without PyPI:

```bash
pip install git+https://github.com/testuser/cloudopti.git
```

This is useful for:
- Testing before PyPI release
- Installing latest development version
- Users who prefer GitHub over PyPI

