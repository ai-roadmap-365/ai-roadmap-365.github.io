#!/bin/bash
# buggy.sh - a deliberately flawed sample for the Day 37 lab.
# It is syntactically valid (bash -n passes) and it runs, yet a linter
# finds real bugs. Treat it as an exhibit to inspect, not code to trust.

name=$1
unused_greeting="Hello there"

if [ $name = "admin" ]; then
  echo "Welcome, admin"
fi

echo "Hi, $name"   
	echo "all done"
