#!/bin/bash

while true; 
do
    python nvidia_stats_json.py;
    sleep 5;
    python NotionAutoUpdateBot.py;
    sleep 300;
done 