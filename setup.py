# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='larus-engine',
    version='0.0.1',
    description=(
        'A sequencer/sampler/synthesizer engine for the Launchpad Mini'
    ),
    long_description=readme,
    author='Beto De Almeida',
    author_email='roberto@dealmeida.net',
    url='https://github.com/robertodealmeida/larus',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
