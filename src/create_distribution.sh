#!/bin/bash

rm -rf dist trajtracker.egg-info build

python setup.py bdist_wheel --universal

