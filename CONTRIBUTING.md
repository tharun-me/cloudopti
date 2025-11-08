# Contributing to CloudOpti

Thank you for your interest in contributing to CloudOpti!

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/testuser/cloudopti.git
   cd cloudopti
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install in development mode:
   ```bash
   pip install -e .
   ```

## Development Guidelines

- Follow PEP 8 style guide
- Add docstrings to all functions and classes
- Write clear commit messages
- Test your changes before submitting

## Submitting Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a Pull Request on GitHub

## Code Structure

- `cloudopti/cli.py` - Command-line interface
- `cloudopti/aws_cost_monitor.py` - Main cost monitoring logic
- `cloudopti/resource_discovery.py` - AWS resource discovery
- `cloudopti/comprehensive_metrics.py` - CloudWatch metrics collection
- `cloudopti/cost_mapper.py` - Cost mapping to resources
- `cloudopti/excel_exporter.py` - Excel report generation
- `cloudopti/enhanced_recommendations.py` - Cost optimization recommendations

## Testing

Before submitting, ensure:
- Code runs without errors
- All imports work correctly
- The `opti aws` command executes successfully

## Questions?

Open an issue on GitHub for any questions or suggestions.

