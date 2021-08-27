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
    name='SCR project API',
    version='1.0',
    packages=find_packages(),
    url='',
    download_url='',
    license='Eclipse Public License 2.0',
    author='David Berrocal Macias',
    author_email='dabm@usal.es',
    description='Flask RESTX API for Service Code Repository Crawler',
    long_description=readme(),
    long_description_content_type='text/markdown',
    install_requires=list(read_requeriments_file('requirements.txt')),
    entry_points={
        'console_scripts': [
            'scr=scr.run:main'
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 1 - Alpha",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Eclipse Public License 2.0",
        "Intended Audience :: Developers"
    ],
    keywords='scr, flask, python',
    python_requires='>=3',
    project_urls={
        'Bug Reports': 'https://github.com/',
        'Source': 'https://github.com/',
        'Documentation': 'https://github.com/'
    },
)