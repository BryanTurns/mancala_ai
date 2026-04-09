#!/bin/bash

echo "Running random vs random"
random_v_random=$(python3 simulate.py --p1 random --p2 random -n 1000)
echo "$random_v_random" | tail -n 5
echo

echo "Running minimax d1 vs random"
minimaxd1_v_random=$(python3 simulate.py --p1 minimax --p1-depth 1 --p2 random -n 1000)
echo "$minimaxd1_v_random" | tail -n 5
echo

echo "Running minimax d2 vs random"
minimaxd2_v_random=$(python3 simulate.py --p1 minimax --p1-depth 2 --p2 random -n 1000)
echo "$minimaxd2_v_random" | tail -n 5
echo

echo "Running minimax d3 vs random"
minimaxd3_v_random=$(python3 simulate.py --p1 minimax --p1-depth 3 --p2 random -n 1000)
echo "$minimaxd3_v_random" | tail -n 5
echo

echo "Running minimax d4 vs random"
minimaxd4_v_random=$(python3 simulate.py --p1 minimax --p1-depth 4 --p2 random -n 1000)
echo "$minimaxd4_v_random" | tail -n 5
echo

echo "Running minimax d5 vs random"
minimaxd5_v_random=$(python3 simulate.py --p1 minimax --p1-depth 5 --p2 random -n 1000)
echo "$minimaxd5_v_random" | tail -n 5
echo
