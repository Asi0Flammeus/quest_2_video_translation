#!/bin/bash

# Check if a parameter is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <path_to_pptx_file>"
    exit 1
fi

# Define paths
PPTX_PATH="$1"
OUTPUT_DIR="$(dirname "$PPTX_PATH")/slides"

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Extract the base name of the PPTX file without the extension
BASE_NAME=$(basename "$PPTX_PATH" .pptx)

# Convert PPTX to PDF using LibreOffice
echo "Converting PPTX to PDF..."
libreoffice --headless --convert-to pdf --outdir "$OUTPUT_DIR" "$PPTX_PATH"
PDF_PATH="${OUTPUT_DIR}/${BASE_NAME}.pdf"
echo "PDF conversion completed."

# Get number of pages in the PDF using pdfinfo
NUM_PAGES=$(pdfinfo "$PDF_PATH" | grep 'Pages' | awk '{print $2}')

# Convert PDF to PNG using ImageMagick's convert
echo "Converting PDF to PNG..."
for ((i=0; i<NUM_PAGES; i++))
do
    echo -ne "Converting page $((i+1)) of $NUM_PAGES...\r"
    convert -density 300 "${PDF_PATH}[$i]" -quality 100 "${OUTPUT_DIR}/${BASE_NAME}_slide_$(printf "%03d" $((i+1))).png"
done
echo -ne "\nConversion to PNG completed. Images saved in ${OUTPUT_DIR}\n"

# Clean up the temporary PDF file
rm "$PDF_PATH"
