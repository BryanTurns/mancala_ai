#!/bin/bash

if [ -z $1 ]; then
	algorithm="alphabeta"
else
	algorithm="$1"
fi

if [ -z $2 ]; then
	count=1000
else
	count="$2"
fi

echo "Running random vs random"
random_v_random=$(python3 simulate.py --p1 random --p2 random -n "$count")
echo "$random_v_random" | tail -n 4
echo

echo "Running $algorithm d1 vs random"
minimaxd1_v_random=$(python3 simulate.py --p1 "$algorithm" --p1-depth 1 --p2 random -n "$count")
echo "$minimaxd1_v_random" | tail -n 4
echo

echo "Running $algorithm d2 vs random"
minimaxd2_v_random=$(python3 simulate.py --p1 "$algorithm" --p1-depth 2 --p2 random -n "$count")
echo "$minimaxd2_v_random" | tail -n 4
echo

echo "Running $algorithm d3 vs random"
minimaxd3_v_random=$(python3 simulate.py --p1 "$algorithm" --p1-depth 3 --p2 random -n "$count")
echo "$minimaxd3_v_random" | tail -n 4
echo

echo "Running $algorithm d4 vs random"
minimaxd4_v_random=$(python3 simulate.py --p1 "$algorithm" --p1-depth 4 --p2 random -n "$count")
echo "$minimaxd4_v_random" | tail -n 4
echo

echo "Running $algorithm d5 vs random"
minimaxd5_v_random=$(python3 simulate.py --p1 "$algorithm" --p1-depth 5 --p2 random -n "$count")
echo "$minimaxd5_v_random" | tail -n 4
echo
