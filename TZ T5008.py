from pdf2image import convert_from_path
import pytesseract
import re
import csv

# Set path to your PDF file
pdf_path = r'C:\Users\andrew\OneDrive - Andrew Chipka\Taxes\2024\8e3b7985-7ce4-4457-8d29-32c3e80ac1a2 - Copy.pdf'
output_csv = r'C:\Users\andrew\OneDrive - Andrew Chipka\Taxes\2024\box20_box21_summary.csv'

# Convert PDF to images
images = convert_from_path(pdf_path, dpi=300)

# OCR the images
full_text = ''
for image in images:
    full_text += pytesseract.image_to_string(image)

# Find monetary values (e.g., 1,234.56)
matches = re.findall(r"(\d{1,3}(?:,\d{3})*\.\d{2})", full_text)

# Extract Box 20 and Box 21 values assuming pattern: quantity, box 20, box 21
results = []
for i in range(0, len(matches) - 2, 3):
    try:
        box_20 = float(matches[i + 1].replace(',', ''))
        box_21 = float(matches[i + 2].replace(',', ''))
        results.append([len(results)+1, box_20, box_21])
    except:
        continue

# Totals
total_box_20 = sum(r[1] for r in results)
total_box_21 = sum(r[2] for r in results)

# Export to CSV
with open(output_csv, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['#', 'Box 20 (Cost/Book Value)', 'Box 21 (Proceeds of Disposition)'])
    writer.writerows(results)
    writer.writerow([])
    writer.writerow(['TOTAL', f'{total_box_20:,.2f}', f'{total_box_21:,.2f}'])

print(f"Export complete! File saved to:\n{output_csv}")
