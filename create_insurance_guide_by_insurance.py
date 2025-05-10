import csv
import os
import glob
from collections import defaultdict
import re

def sanitize_filename(name):
    """Sanitize a string to be used as a filename."""
    # First sanitize the name
    name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip('_')
    
    # If name is too long (over 100 characters), truncate it
    if len(name) > 100:
        # Keep first 50 chars and last 50 chars, separated by underscore
        name = name[:50] + '_' + name[-50:]
    
    return name if name else "default_filename"

def main():
    output_dir = "insurance_docs"
    os.makedirs(output_dir, exist_ok=True)

    # CSVs that have an extra 4th column before doctor names start
    csvs_with_extra_location_column = [
        "US Eye Insurance Guide(Center for Sight).csv",
        "US Eye Insurance Guide(SW FL Eye).csv",
        "US Eye Insurance Guide(Center for Sight-Naples).csv"
    ]

    all_csv_files = [f for f in glob.glob("*.csv") if not f.endswith("Zone.Identifier")]    
    other_csv_files = [f for f in all_csv_files if f not in ["Insurance_FAQ.csv"]]

    # Dictionary to store insurance plan data
    insurance_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for csv_file in other_csv_files:
        location = os.path.splitext(csv_file)[0].replace("_", " ")
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
            except StopIteration:
                continue
            
            headers = [header.strip('\ufeff').strip() for header in headers]

            # Determine where doctor columns start
            doctor_column_start_index = 3
            if csv_file in csvs_with_extra_location_column:
                if len(headers) > 3 and headers[3] == "Is this plan only accepted at specific practice locations?":
                    doctor_column_start_index = 4

            if len(headers) <= doctor_column_start_index:
                continue

            doctor_column_names = headers[doctor_column_start_index:]
            
            for row in reader:
                if not row or not any(cell.strip() for cell in row):
                    continue
                
                plan_name = row[0].strip() if len(row) > 0 else ""
                nextgen_name = row[1].strip() if len(row) > 1 else ""
                referral_auth = row[2].strip() if len(row) > 2 else ""
                
                if not plan_name:  # Skip rows without insurance plan name
                    continue

                for i, doctor_name_header in enumerate(doctor_column_names):
                    doctor_name = doctor_name_header.strip()
                    status_index = i + doctor_column_start_index
                    status = row[status_index].strip() if len(row) > status_index else ""
                    
                    if doctor_name and status:  # Only store if both doctor name and status exist
                        insurance_data[plan_name][location][doctor_name].append({
                            'nextgen_name': nextgen_name,
                            'referral_auth': referral_auth,
                            'status': status
                        })

    # Generate individual insurance plan files and collect links
    insurance_files_links = []
    summary_insurance_entries = []
    processed_insurances = set()  # Track unique insurance names

    for insurance_name in sorted(insurance_data.keys()):
        # Skip if we've already processed this insurance name
        if insurance_name in processed_insurances:
            continue
        processed_insurances.add(insurance_name)
        
        safe_insurance_name = sanitize_filename(insurance_name)
        insurance_filename = f"{safe_insurance_name}.md"
        insurance_filepath = os.path.join(output_dir, insurance_filename)
        
        # Add link for Insurance_Guide_By_Insurance.md
        insurance_files_links.append(f"* [{insurance_name}]({output_dir}/{insurance_filename})")
        
        # Add entry for SUMMARY.md
        summary_insurance_entries.append(f"  * [{insurance_name}]({output_dir}/{insurance_filename})")

        with open(insurance_filepath, "w", encoding='utf-8') as insurance_outfile:
            insurance_outfile.write(f"# {insurance_name} - Insurance Guide\n\n")
            insurance_outfile.write(f"*This page lists providers who accept {insurance_name}, grouped by location.*\n\n")
            
            insurance_outfile.write(f"<details open><summary>Provider Details for {insurance_name}</summary>\n\n")
            
            for location in sorted(insurance_data[insurance_name].keys()):
                insurance_outfile.write(f"## {location}\n\n")
                insurance_outfile.write("| Provider | NextGen Name | Referral/Auth | Status |\n")
                insurance_outfile.write("|----------|-------------|--------------|--------|\n")
                
                for doctor_name, details_list in sorted(insurance_data[insurance_name][location].items()):
                    for details in details_list:
                        doctor_name_escaped = doctor_name.replace("|", "\\|")
                        nextgen_name_escaped = details['nextgen_name'].replace("|", "\\|")
                        referral_auth_escaped = details['referral_auth'].replace("|", "\\|")
                        status_escaped = details['status'].replace("|", "\\|")
                        insurance_outfile.write(f"| {doctor_name_escaped} | {nextgen_name_escaped} | {referral_auth_escaped} | {status_escaped} |\n")
                
                insurance_outfile.write("\n")
            
            insurance_outfile.write("</details>\n\n")

    # Create the main Insurance Guide By Insurance file
    with open("Insurance_Guide_By_Insurance.md", "w", encoding='utf-8') as outfile:
        outfile.write("# Insurance Guide By Insurance Plan\n\n")
        outfile.write("*This guide lists insurance participation by insurance plan. Click an insurance plan to view all providers who accept that insurance, grouped by location.*\n\n")
        outfile.write("\n".join(insurance_files_links))
        outfile.write("\n\n")

        # Add FAQ section if it exists
        if os.path.exists("Insurance_FAQ.csv"):
            outfile.write("## Insurance FAQ\n\n")
            with open("Insurance_FAQ.csv", 'r', encoding='utf-8') as f_faq:
                reader_faq = csv.reader(f_faq)
                try:
                    headers_faq = next(reader_faq)
                except StopIteration:
                    headers_faq = []
                
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

    # Update SUMMARY.md
    summary_path = "SUMMARY.md"
    provider_guide_title = "* [Insurance Guide By Provider](<Insurance_Guide_By_Provider.md>)"
    insurance_guide_title = "* [Insurance Guide By Insurance](<Insurance_Guide_By_Insurance.md>)"
    
    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f_summary:
            summary_lines = f_summary.readlines()

        new_summary_lines = []
        provider_section_found = False
        insurance_section_found = False
        i = 0
        while i < len(summary_lines):
            line = summary_lines[i]
            # Skip old provider or insurance sub-entries
            if line.strip() == provider_guide_title.strip():
                provider_section_found = True
                new_summary_lines.append(provider_guide_title + "\n")
                i += 1
                # Skip any existing indented provider entries
                while i < len(summary_lines) and summary_lines[i].startswith("  * "):
                    i += 1
                continue
            elif line.strip() == insurance_guide_title.strip():
                insurance_section_found = True
                new_summary_lines.append(insurance_guide_title + "\n")
                i += 1
                # Skip any existing indented insurance entries
                while i < len(summary_lines) and summary_lines[i].startswith("  * "):
                    i += 1
                continue
            new_summary_lines.append(line)
            i += 1
        # If not found, add at the end in the correct order
        if not provider_section_found:
            new_summary_lines.append(provider_guide_title + "\n")
        if not insurance_section_found:
            new_summary_lines.append(insurance_guide_title + "\n")
        with open(summary_path, "w", encoding="utf-8") as f_summary:
            f_summary.writelines(new_summary_lines)
    else:
        print(f"Warning: {summary_path} not found. Insurance links not added to SUMMARY.md.")

if __name__ == "__main__":
    main() 