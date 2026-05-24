#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/onkohelper
python3 -m pytest onkohelper/tests/
