#!/bin/bash

# Path to the CSV file
csv_file="/etc/restream/streams.csv"

while true; do
    # Read streams.csv line by line
    while IFS=, read -r input alias; do
        # Check if input has a video stream
        if ffprobe -v error -select_streams v -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "$input" >/dev/null 2>&1; then

            echo "restreaming $input to rtsp://localhost:8554/$alias"

            # Restream video stream
            ffmpeg -i "$input" -c copy -f rtsp rtsp://localhost:8554/"$alias"
        else
            
            echo "no video stream found in $input, trying again in 5 seconds"
            # Wait for a while before checking again
            sleep 5
        fi
    done < "$csv_file"
done