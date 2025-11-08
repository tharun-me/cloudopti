# Installation Guide

## Installation from PyPI (Recommended)

Once published to PyPI, install CloudOpti globally using pip:

```bash
pip install cloudopti
```

After installation, you can run the tool from anywhere:

```bash
opti aws
```

## Installation from GitHub

### Option 1: Install directly from GitHub

```bash
pip install git+https://github.com/testuser/cloudopti.git
```

### Option 2: Clone and install

```bash
# Clone the repository
git clone https://github.com/testuser/cloudopti.git
cd cloudopti

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

## Installation from Source (Development)

For development or if you want to modify the code:

```bash
# Clone the repository
git clone https://github.com/testuser/cloudopti.git
cd cloudopti

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode
pip install -e .
```

## Verify Installation

After installation, verify that the tool is installed correctly:

```bash
opti --help
```

You should see:
```
usage: opti [-h] {aws} ...

CloudOpti - AWS Cost Monitoring Tool

positional arguments:
  {aws}       Service to monitor
    aws       Monitor AWS costs
```

## Requirements

- Python 3.8 or higher
- AWS credentials configured (`aws configure`)
- Required AWS permissions (see README.md)

## Troubleshooting

### Command not found

If `opti` command is not found after installation:

1. Check if pip installed to a location in your PATH:
   ```bash
   pip show cloudopti
   ```

2. On Linux/Mac, you may need to add pip's bin directory to PATH:
   ```bash
   export PATH=$PATH:~/.local/bin
   ```

3. On Windows, ensure Python Scripts directory is in PATH:
   ```bash
   # Usually: C:\Users\YourUsername\AppData\Local\Programs\Python\Python3X\Scripts
   ```

### Permission errors

If you get permission errors, use `--user` flag:

```bash
pip install --user cloudopti
```

Or use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install cloudopti
```

