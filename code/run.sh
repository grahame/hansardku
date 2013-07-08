#!/bin/zsh

dropdb hansardku
createdb hansardku && ./hansardku.py $*

