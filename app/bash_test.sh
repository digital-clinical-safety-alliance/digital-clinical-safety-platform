#!/bin/bash

# Define the two lists
dockerFiles=("dockerfiles/app/Dockerfile" "dockerfiles/app/Packages" "dockerfiles/app/requirements.txt" "grape")
list2=("kiwi" "orange" "pear" "grape")

# Compare the lists
matching_values=()

for item in "${list1[@]}"; do
    if [[ " ${list2[@]} " =~ " $item " ]]; then
        matching_values+=("$item")
    fi
done

# Check if there are matching values
if [ ${#matching_values[@]} -gt 0 ]; then
    echo "Error: Matching values found: ${matching_values[@]}"
    exit 1
else
    echo "Lists do not contain matching values."
fi