#!/bin/bash
n="$1";
max="$2";
while [ "$n" -le "$max" ]; do
  mkdir "$n"
  n=`expr "$n" + 1`;
done