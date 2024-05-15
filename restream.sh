#!/bin/bash

# Path to the CSV file
csv_file="/etc/restream/streams.csv"

# Read the CSV file line by line
while IFS=',' read -r input alias
do
    # Process each entry
    echo "input: $input, alias: $alias"

    # use ffmpeg to restream rtsp stream to rtsp
    ffmpeg -i $input -c copy -f rtsp rtsp://localhost:8554/$alias
    
done < "$csv_file"