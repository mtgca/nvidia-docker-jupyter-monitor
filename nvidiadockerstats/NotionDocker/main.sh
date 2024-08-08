#!/bin/bash

while true; 
do
    python jupytertoken_extraction.py;
    sleep 5;
    python NotionAutoUpdateBot.py;
    sleep 240;
done 