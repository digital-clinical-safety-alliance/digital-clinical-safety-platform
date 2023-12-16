#!/bin/bash

trap printout EXIT

exitFunction() {
    exit
}

while :
do
    ((count++))
    sleep 1
done