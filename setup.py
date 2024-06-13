#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("requirements_dev.txt") as f:
    requirements_dev = f.read().splitlines()

setup(
    author="Todd Miller",
    author_email='jmiller@stsci.edu',
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    description="Translate and run shellscript doctests as Python doctests.",
    entry_points={
        'console_scripts': [
            'sh-doctest=sh_doctest.cli:main',
        ],
    },
    install_requires=requirements,
    license="BSD license",
    long_description=readme,
    include_package_data=True,
    keywords='sh_doctest',
    name='sh-doctest',
    packages=find_packages(include=['sh_doctest', 'sh_doctest.*']),
    test_suite='tests',
    tests_require=requirements_dev,
    # url='https://github.com/jaytmiller/sh_doctest',
    version='0.1.0',
    zip_safe=False,
)
