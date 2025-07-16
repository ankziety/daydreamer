#!/usr/bin/env python3
"""
Setup script for Daydreamer Project
Default mode network AI simulation using Gemma 3N and Ollama
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="daydreamer",
    version="0.1.0",
    author="Daydreamer Team",
    author_email="team@daydreamer.ai",
    description="Default mode network AI simulation using Gemma 3N and Ollama",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/daydreamer-ai/daydreamer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "full": [
            "numpy>=1.21.0",
            "pandas>=1.3.0",
            "matplotlib>=3.4.0",
            "websockets>=10.0",
            "fastapi>=0.68.0",
            "uvicorn>=0.15.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "daydreamer=src.main:main",
            "daydreamer-demo=src.simulation.multi_agent_simulation:demo_multi_agent_simulation",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md", "*.txt"],
    },
    keywords="ai, artificial-intelligence, agents, default-mode-network, gemma3n, ollama, simulation",
    project_urls={
        "Bug Reports": "https://github.com/daydreamer-ai/daydreamer/issues",
        "Source": "https://github.com/daydreamer-ai/daydreamer",
        "Documentation": "https://github.com/daydreamer-ai/daydreamer/blob/main/README.md",
    },
)