import csv
import os
import glob

def generate_markdown_for_csv(csv_file, transpose_threshold=7):
    """Convert a CSV file to a Markdown section.
    If columns > transpose_threshold, transpose to key-value format per row.
    Otherwise, render as a standard Markdown table.
    """
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        # Store rows to allow multiple passes if needed (e.g., for transposing)
        data_rows = list(reader)
        
        if not headers: # Empty CSV
            return ""
            
        # Clean header names (e.g., remove leading/trailing whitespace, BOM if any on first header)
        headers = [header.strip('\ufeff').strip() for header in headers]

        if len(headers) > transpose_threshold and csv_file != "Insurance_FAQ.csv":
            # Transpose: Each original row becomes a section with a key-value table
            markdown_sections = []
            for row_index, row in enumerate(data_rows):
                if not row or not any(cell.strip() for cell in row): # Skip empty or effectively empty rows
                    continue
                
                # Use the content of the first cell as the sub-heading
                # Ensure there's content in the first cell to form a heading
                first_cell_content = str(row[0]).replace("|", "\\|").strip()
                if not first_cell_content:
                    # If first cell is empty, create a generic heading for the row
                    first_cell_content = f"Record {row_index + 1}"

                section = f"### {first_cell_content}\n\n"
                section += "| Attribute | Value |\n"
                section += "|-----------|-------|\n"
                
                for i, header in enumerate(headers):
                    # Skip the first header if its value is used for the section title,
                    # unless it's the only header. Handle if row is shorter than headers.
                    if i == 0 and len(headers) > 1: 
                        # If we use the first column for the heading, start attributes from the second column.
                        # However, let's list all attributes for clarity, including the one used for heading.
                        # Or, if preferred, we can start from headers[1]
                        pass # Continue to list all, or adjust logic here if needed.

                    cell_value = str(row[i]).replace("|", "\\|").strip() if i < len(row) else ""
                    section += f"| {header.replace('|', '\\|').strip()} | {cell_value} |\n"
                markdown_sections.append(section)
            return "\n".join(markdown_sections)
        else:
            # Standard table rendering (for FAQ or narrow tables)
            markdown = "| " + " | ".join(headers) + " |\n"
            markdown += "| " + " | ".join([":--"] * len(headers)) + " |\n" # Use :-- for left alignment
            
            for row in data_rows:
                if not row or not any(cell.strip() for cell in row): # Skip empty rows
                    continue
                cleaned_row = [str(cell).replace("|", "\\|").strip() for cell in row]
                # Ensure row has same number of cells as headers, pad if necessary
                while len(cleaned_row) < len(headers):
                    cleaned_row.append("")
                markdown += "| " + " | ".join(cleaned_row) + " |\n"
            return markdown

def main():
    # Get all CSV files except those with Zone.Identifier
    csv_files = [f for f in glob.glob("*.csv") if not f.endswith("Zone.Identifier")]
    
    # Create the output file
    with open("Insurance_Guide.md", "w", encoding="utf-8") as outfile:
        outfile.write("# Insurance Guide\n\n")
        
        if "Insurance_FAQ.csv" in csv_files:
            outfile.write("## Insurance FAQ\n\n")
            # FAQ should always be a normal table, ensure transpose_threshold doesn't affect it
            # or handle it specifically like this:
            with open("Insurance_FAQ.csv", 'r', encoding='utf-8') as f_faq:
                reader_faq = csv.reader(f_faq)
                headers_faq = next(reader_faq)
                headers_faq = [header.strip('\ufeff').strip() for header in headers_faq]
                data_rows_faq = list(reader_faq)

                md_table = "| " + " | ".join(headers_faq) + " |\n"
                md_table += "| " + " | ".join([":--"] * len(headers_faq)) + " |\n"
                for r in data_rows_faq:
                    if not r or not any(cell.strip() for cell in r): continue
                    cleaned_r = [str(c).replace("|", "\\|").strip() for c in r]
                    while len(cleaned_r) < len(headers_faq): cleaned_r.append("")
                    md_table += "| " + " | ".join(cleaned_r) + " |\n"
                outfile.write(md_table)

            outfile.write("\n\n")
            csv_files.remove("Insurance_FAQ.csv")
        
        csv_files.sort()
        
        for csv_file in csv_files:
            section_name = os.path.splitext(csv_file)[0].replace("_", " ") # Make title more readable
            outfile.write(f"## {section_name}\n\n")
            
            # Pass transpose_threshold, default is 7
            markdown_content = generate_markdown_for_csv(csv_file) 
            outfile.write(markdown_content)
            outfile.write("\n\n")

if __name__ == "__main__":
    main() 