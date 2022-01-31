#!/usr/bin/python3
# Eclipse Public License 2.0

import io
from setuptools import setup, find_packages

def readme():
    with io.open('README.md', encoding='utf-8') as f:
        return f.read()

def read_requeriments_file(filename):
    with io.open(filename, encoding='utf-8') as f:
        for line in f.readlines():
            yield line.strip()

setup(
    name='Service Discovery API - SmartCLIDE',
    version='1.0',
    packages=find_packages(),
    url='',
    download_url='https://github.com/eclipse-researchlabs/smartclide-service-discovery-poc/archive/refs/heads/main.zip',
    license='Eclipse Public License 2.0',
    author='AIR Institute',
    author_email='dabm@air-institute.org',
    description='Flask RESTX API for Service Discovery - SmartCLIDE',
    long_description=readme(),
    long_description_content_type='text/markdown',
    install_requires=list(read_requeriments_file('requirements.txt')),
    entry_points={
        'console_scripts': [
            'servicediscovery=servicediscovery.run:main'
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 1.0 - Alpha",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Eclipse Public License 2.0",
        "Intended Audience :: Developers"
    ],
    keywords='scr, flask, python',
    python_requires='>=3',
    project_urls={
        'Bug Reports': 'https://github.com/eclipse-researchlabs/smartclide-service-discovery-poc/issues',
        'Source': 'https://github.com/eclipse-researchlabs/smartclide-service-discovery-poc',
        'Documentation': 'https://github.com/eclipse-researchlabs/smartclide-service-discovery-poc/blob/main/README.md'
    },
)