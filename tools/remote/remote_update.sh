#!/bin/bash

cd ~/deepThought/
git reset --hard
git pull
cd tooling/

sudo pypy setup.py install
