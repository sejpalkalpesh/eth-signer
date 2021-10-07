#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

extras_require = {
    'eth-signer':[
        "eth-utils>=1.8.2,<2.0.0",
        "eth-typing>=2.2.1,<3.0.0",
        "hexbytes>=0.1.0,<1",
        "eth-keys>=0.3.1",
        "eth_account>=0.5.5"
        "eth-rlp>=0.1.2,<2",
        "pycryptodome>=3.6.6,<4",
        "boto3>=1.18.42,<1.19.0",
    ],
    'test': [
        "pytest==5.4.1",
    ],
    'lint': [
        "flake8==3.8.3",
        "isort>=4.2.15,<4.3.5",
        "mypy==0.812",
    ],
    'docs': [
        "Sphinx>=1.6.5,<2",
        "sphinx_rtd_theme>=0.1.9,<2",
        "towncrier>=19.2.0, <20",
    ],
    'dev': [
        "bumpversion==0.5.3",
        "setuptools>=38.6.0",
        "tox>=1.8.0",
        "twine>=1.13,<2",
    ]
}

extras_require['dev'] = (
    extras_require['test']
    + extras_require['lint']
    + extras_require['docs']
    + extras_require['dev']
)

with open('./README.md') as readme:
    long_description = readme.read()

setup(
    name='eth-signer',
    # *IMPORTANT*: Don't manually change the version here. Use `make bump`, as described in readme
    version='0.1.8',
    description="""A Python library for transection signing using AWS Key Management Service.""",
    long_description_content_type='text/markdown',
    long_description=long_description,
    author='Kalpesh Sejpal',
    author_email='sejpalkalpesh@gmail.com',
    url='https://github.com/sejpalkalpesh/eth-signer',
    include_package_data=True,
    install_requires=extras_require['eth-signer'],
    python_requires='>=3.6,<4',
    extras_require=extras_require,
    py_modules=['eth_signer'],
    license="MIT",
    zip_safe=False,
    keywords='ethereum AWS KMS,',
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={"eth_signer": ["py.typed"]},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
