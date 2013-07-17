#!/bin/zsh

dropdb hansardku
createdb hansardku && ./hansardku.py $*
psql hansardku < search.sql

