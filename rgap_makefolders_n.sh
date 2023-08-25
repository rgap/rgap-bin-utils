#!/bin/bash
n_ini="$1"
n_end="$2"
while [ "$n_ini" -le "$n_end" ]; do
  mkdir "$n_ini"
  n_ini=$(expr "$n_ini" + 1)
done
