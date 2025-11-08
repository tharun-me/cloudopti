from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cloudopti",
    version="2.0.0",
    author="CloudOpti Team",
    author_email="cloudopti@example.com",  # Update with your email
    description="AWS Cost Monitoring and Optimization Tool - Similar to Prowler but for cost optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/testuser/cloudopti",  # Update with your GitHub URL
    project_urls={
        "Bug Tracker": "https://github.com/testuser/cloudopti/issues",
        "Documentation": "https://github.com/testuser/cloudopti#readme",
        "Source Code": "https://github.com/testuser/cloudopti",
    },
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "opti=cloudopti.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="aws, cost, optimization, monitoring, cloudwatch, ec2, s3, rds, eks, cost-savings",
)
