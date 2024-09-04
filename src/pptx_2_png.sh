#!/bin/bash

# Define paths
PPTX_PATH="../test/lnp201-en.pptx"
OUTPUT_DIR="../test/"

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Extract the base name of the PPTX file without the extension or path
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
