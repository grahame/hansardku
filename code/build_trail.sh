#!/bin/zsh

echo 'drop table haiku_trail_entry; drop table haiku_trial;' | psql hansardku
./hansardtrail.py

