#!/bin/bash

dropdb hansardku
createdb hansardku && ./hansardku.py $*

