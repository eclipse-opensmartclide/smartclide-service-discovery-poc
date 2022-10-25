# *******************************************************************************
# Copyright (C) 2022 AIR Institute
#
# This program and the accompanying materials are made
# available under the terms of the Eclipse Public License 2.0
# which is available at https://www.eclipse.org/legal/epl-2.0/
#
# SPDX-License-Identifier: EPL-2.0
#
# Contributors:
#    David Berrocal Macías (@dabm-git) - initial API and implementation
# *******************************************************************************

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
    name='SmartCLIDE - Service Discovery API',
    version='1.0',
    packages=find_packages(),
    url='',
    download_url='https://github.com/eclipse-opensmartclide/smartclide-service-discovery-poc/archive/refs/heads/main.zip',
    license='Eclipse Public License 2.0',
    author='David Berrocal Macías - AIR Institute',
    author_email='dberrocal@air-institute.com',
    description='SmartCLIDE - Flask RESTX API for Service Discovery',
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
        'Bug Reports': 'https://github.com/eclipse-opensmartclide/smartclide-service-discovery-poc/issues',
        'Source': 'https://github.com/eclipse-opensmartclide/smartclide-service-discovery-poc',
        'Documentation': 'https://github.com/eclipse-opensmartclide/smartclide-service-discovery-poc/blob/main/README.md'
    },
)
