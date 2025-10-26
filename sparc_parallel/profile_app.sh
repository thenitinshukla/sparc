#!/bin/bash

# Usage:
# ./profile_app.sh <binary> "<input_args>" <project_dir>

# Check arguments
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <binary> \"<input_args>\" <project_dir>"
    exit 1
fi

BINARY=$1
INPUT_ARGS=$2
PROJECT_DIR=$3

# Create project directory if it doesn't exist
mkdir -p "$PROJECT_DIR"

echo "=== Starting VTune profiling ==="
# VTune: Hotspots analysis to see which part of code takes more time
vtune -collect hotspots -result-dir "$PROJECT_DIR/vtune_hotspots" -- "$BINARY" $INPUT_ARGS

echo "=== VTune analysis done. ==="
echo "Result directory: $PROJECT_DIR/vtune_hotspots"

echo "=== Starting Intel Advisor Survey collection ==="
advisor --collect=survey --project-dir="$PROJECT_DIR/advisor_survey" -- "$BINARY" $INPUT_ARGS
echo "Survey collection done."

echo "=== Starting Intel Advisor Trip Counts collection ==="
advisor --collect=tripcounts --project-dir="$PROJECT_DIR/advisor_tripcounts" -- "$BINARY" $INPUT_ARGS
echo "Trip counts collection done."

echo "=== Starting Intel Advisor Roofline collection ==="
advisor --collect=roofline \
        --stacks \
        --enable-cache-simulation \
        --cache-config=auto \
        --project-dir="$PROJECT_DIR/advisor_roofline" \
        -- "$BINARY" $INPUT_ARGS
echo "Roofline collection done."

echo "=== Generating Roofline report ==="
advisor --report=roofline \
        --stacks \
        --enable-cache-simulation \
        --cache-config=auto \
        --project-dir="$PROJECT_DIR/advisor_roofline" \
        --report-output="$PROJECT_DIR/roofline.html"
echo "Roofline report saved to $PROJECT_DIR/roofline.html"

echo "=== Profiling complete! ==="
echo "VTune results: $PROJECT_DIR/vtune_hotspots"
echo "Advisor Survey: $PROJECT_DIR/advisor_survey"
echo "Advisor Trip Counts: $PROJECT_DIR/advisor_tripcounts"
echo "Advisor Roofline: $PROJECT_DIR/advisor_roofline"

