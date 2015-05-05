# -*- coding: utf-8-*-
from setuptools import setup, find_packages
setup(
name='deepThought',
version='0.0.0',
author='Julius Flohr',
author_email='julius.flohr@gmail.com',
packages=find_packages(),
url='https://github.com/juliusf/deepThought',
description='The Answer to The Ultimate Question of Life, the Universe and Everything.',
long_description=open('README.md').read(),
scripts=['bin/extractor', 'bin/simulator', 'bin/visualizer', 'bin/multisim', 'bin/optimizer']
)