#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = []

with open('requirements.txt') as f:
    for line in f.readlines():
        req = line.strip()
        if not req or req.startswith('#') or '://' in req:
            continue
        install_requires.append(req)

setup(
    name='rodentVR',
    description='rodentVR is a Python 3-based virtual reality system '
                'tailored specifically to neuroscience research.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/simonarvin/rodentVR',
    license='GPL',
    license_file='LICENSE',
    platforms='any',
    python_requires='>=3.7',
    version='0.1',
    entry_points={
        'console_scripts': [
            'rodentVR=rodentVR.run_rodentVR:main'
        ]
    },
    packages=find_packages(include=["rodentVR*"]),
    include_package_data=True,
    install_requires=install_requires,
    project_urls={
        "Documentation": "https://github.com/simonarvin/rodentVR",
        "Source": "https://github.com/simonarvin/rodentVR",
        "Tracker": "https://github.com/simonarvin/rodentVR/issues"
    }
)
