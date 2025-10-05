#!/usr/bin/env python3
# setup.py
"""
Setup script for Clash Finder application.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ''

# Read requirements
requirements_file = Path(__file__).parent / 'requirements.txt'
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith('#')
        ]

setup(
    name='clash-finder',
    version='1.0.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='League of Legends player statistics and Clash team finder',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/clash-finder',
    packages=find_packages(exclude=['tests', 'tests.*', 'docs']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Games/Entertainment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: Flask',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.4.3',
            'pytest-flask>=1.3.0',
            'pytest-cov>=4.1.0',
            'black>=23.12.1',
            'flake8>=6.1.0',
            'isort>=5.13.2',
            'mypy>=1.7.1',
        ],
        'redis': [
            'redis>=5.0.1',
            'hiredis>=2.2.3',
        ],
        'production': [
            'gunicorn>=21.2.0',
            'gevent>=23.9.1',
        ],
    },
    entry_points={
        'console_scripts': [
            'clash-finder=run:main',
        ],
    },
    include_package_data=True,
    package_data={
        'app': [
            'templates/**/*.html',
            'static/**/*',
        ],
    },
    zip_safe=False,
    keywords='league-of-legends lol riot-api clash statistics flask',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/clash-finder/issues',
        'Source': 'https://github.com/yourusername/clash-finder',
        'Documentation': 'https://github.com/yourusername/clash-finder/wiki',
    },
)