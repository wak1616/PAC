import csv
import os
import glob
from collections import defaultdict

def generate_markdown_for_csv(csv_file, transpose_threshold=1):
    """Convert a CSV file to a Markdown section.
    If columns > transpose_threshold, transpose to key-value format per row,
    wrapped in <details>/<summary> tags.
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

                # Start with <details> and <summary>
                section = f"<details><summary>{first_cell_content}</summary>\n\n"
                
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
                
                section += "\n</details>" # Close <details>
                markdown_sections.append(section)
            return "\n\n".join(markdown_sections) # Add double newline between details sections for spacing
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
    # CSVs that have an extra 4th column before doctor names start
    csvs_with_extra_location_column = [
        "US Eye Insurance Guide(Center for Sight).csv",
        "US Eye Insurance Guide(SW FL Eye).csv",
        "US Eye Insurance Guide(Center for Sight-Naples).csv"
    ]

    all_csv_files = [f for f in glob.glob("*.csv") if not f.endswith("Zone.Identifier")]    
    other_csv_files = [f for f in all_csv_files if f not in ["Insurance_FAQ.csv"]]

    doctor_data = defaultdict(lambda: defaultdict(list))

    for csv_file in other_csv_files:
        location = os.path.splitext(csv_file)[0].replace("_", " ") # Cleaner location name
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
            except StopIteration: # Skip empty CSVs
                continue
            
            headers = [header.strip('\ufeff').strip() for header in headers]

            # Determine where doctor columns start
            doctor_column_start_index = 3 # Default for files like Retina, Lake Eye
            if csv_file in csvs_with_extra_location_column:
                if len(headers) > 3 and headers[3] == "Is this plan only accepted at specific practice locations?":
                    doctor_column_start_index = 4
                # else: could add a warning or error if structure is unexpected
            
            if len(headers) <= doctor_column_start_index: # No doctor columns found based on logic
                continue

            doctor_column_names = headers[doctor_column_start_index:]
            
            for row in reader:
                if not row or not any(cell.strip() for cell in row):
                    continue
                
                plan_name = row[0].strip() if len(row) > 0 else ""
                nextgen_name = row[1].strip() if len(row) > 1 else ""
                referral_auth = row[2].strip() if len(row) > 2 else ""
                
                for i, doctor_name_header in enumerate(doctor_column_names):
                    doctor_name = doctor_name_header.strip() # Use the cleaned header as doctor name
                    # Data for doctors starts from doctor_column_start_index in the row
                    status_index = i + doctor_column_start_index
                    status = row[status_index].strip() if len(row) > status_index else ""
                    
                    if doctor_name: # Ensure doctor name is not empty
                        doctor_data[doctor_name][location].append((plan_name, nextgen_name, referral_auth, status))

    with open("Insurance_Guide.md", "w", encoding="utf-8") as outfile:
        outfile.write("# Insurance Guide\n\n")
        outfile.write("*This guide lists insurance participation by doctor. Click a doctor's name to view all insurance info for that doctor, grouped by location/CSV.*\n\n")
        
        for doctor_name_key in sorted(doctor_data.keys()):
            locations_dict = doctor_data[doctor_name_key]
            location_names = list(locations_dict.keys())
            locations_str = ", ".join(sorted(location_names)) # Sort location names for consistent summary
            
            outfile.write(f"<details><summary>{doctor_name_key} ({locations_str})</summary>\n\n")
            for loc_name in sorted(locations_dict.keys()): # Iterate in sorted order for consistency
                outfile.write(f"#### {loc_name}\n\n")
                outfile.write("| Insurance Plan Name | NextGen Name | Referral/Auth | Status |\n")
                outfile.write("|--------------------|-------------|--------------|--------|\n")
                for plan_name, nextgen_name, referral_auth, status in locations_dict[loc_name]:
                    plan_name_escaped = plan_name.replace("|", "\\|")
                    nextgen_name_escaped = nextgen_name.replace("|", "\\|")
                    referral_auth_escaped = referral_auth.replace("|", "\\|")
                    status_escaped = status.replace("|", "\\|")
                    outfile.write(f"| {plan_name_escaped} | {nextgen_name_escaped} | {referral_auth_escaped} | {status_escaped} |\n")
                outfile.write("\n")
            outfile.write("</details>\n\n")

        if os.path.exists("Insurance_FAQ.csv"):
            outfile.write("## Insurance FAQ\n\n")
            with open("Insurance_FAQ.csv", 'r', encoding='utf-8') as f_faq:
                reader_faq = csv.reader(f_faq)
                try:
                    headers_faq = next(reader_faq)
                except StopIteration:
                    headers_faq = [] # Handle empty FAQ CSV
                
                if headers_faq:
                    headers_faq = [header.strip('\ufeff').strip() for header in headers_faq]
                    data_rows_faq = list(reader_faq)
                    md_table = "| " + " | ".join(headers_faq) + " |\n"
                    md_table += "| " + " | ".join([":--"] * len(headers_faq)) + " |\n"
                    for r_faq in data_rows_faq:
                        if not r_faq or not any(cell.strip() for cell in r_faq): continue
                        cleaned_r_faq = [str(c).replace("|", "\\|").strip() for c in r_faq]
                        while len(cleaned_r_faq) < len(headers_faq): cleaned_r_faq.append("")
                        md_table += "| " + " | ".join(cleaned_r_faq) + " |\n"
                    outfile.write(md_table)
                    outfile.write("\n")

if __name__ == "__main__":
    main() 