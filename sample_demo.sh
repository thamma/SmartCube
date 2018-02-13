#!/bin/bash
# This script executes the pipeline. Below pieces can easily be interchanged
reader/read_characteristic | python parser/parser.py | python sample_application.py
