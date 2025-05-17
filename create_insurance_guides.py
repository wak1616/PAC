import pandas as pd
import os
from collections import defaultdict
import re
from datetime import datetime

def sanitize_filename(name):
    """Sanitize a string to be used as a filename."""
    name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip('_')
    if len(name) > 100: # Truncate if too long
        name = name[:50] + '_' + name[-50:]
    return name if name else "default_filename"

def generate_markdown_for_faq(faq_df):
    """Generates Markdown table for FAQ data from a DataFrame."""
    if faq_df.empty:
        return ""
    
    headers = [str(header).strip('\ufeff').strip() for header in faq_df.columns.tolist()]
    data_rows = faq_df.values.tolist()

    if not headers:
        return ""

    md_table = "| " + " | ".join(headers) + " |\n"
    md_table += "| " + " | ".join([":--"] * len(headers)) + " |\n"
    for row_data in data_rows:
        row = [str(cell) for cell in row_data] 
        if not row or not any(cell.strip() for cell in row): continue
        cleaned_r_faq = [str(c).replace("|", "\\|").strip() for c in row]
        while len(cleaned_r_faq) < len(headers): cleaned_r_faq.append("")
        md_table += "| " + " | ".join(cleaned_r_faq) + " |\n"
    return md_table

def generate_status_legend():
    """Generates Markdown content for the status legend."""
    legend_content = """
## Status Legend

<div class="status-legend">
<p><strong>PAR</strong>: Participating (PAR) providers contract with the patient's health plan. There is a direct contract between the provider/practice and an insurance company that allows our claims to be processed and paid, based on our contracted amounts negotiated per CPT code. Patients save a considerable amount of money when they are seen by a participating provider than a non-participating provider.</p>

<p><strong>Non-PAR-OON Benefits</strong>: If a patient has a plan NON-PAR or OON, they may have OON benefits. OON benefits may be available with PPO plans. OON with benefits means that the insurance company will pay us based on usual and customary (U&C), but not based on a contract since the provider/practice does not have a direct contract with the payer. If the patient has OON benefits, the insurance typically applies a higher benefit (i.e., copay is $40 to see a participating provider, but may increase to $75 due to OON, etc.)</p>

<p><strong>Non-PAR</strong>: Non-participating (NON-PAR) means the provider/practice does not have a contract with the patient's health plan. This is also called a non-preferred provider or OUT-OF-NETWORK (OON). If the patient chooses to be seen by a non-participating provider, the patient will pay more as a self-pay patient. OON plans may or may not have OON benefits. HMO plans do not have OON benefits, therefore, the patient must be seen as self-pay.</p>
</div>

"""
    return legend_content

# Note: generate_markdown_for_excel_sheet_data is not directly used as provider/insurance page structures differ.
# Specific markdown generation logic is kept within their respective generation functions.

def find_latest_excel_file(directory):
    """
    Finds the Excel file in the given directory that matches the pattern
    "US Eye Insurance Guide_MMDDYY.xlsx" and has the latest date.
    """
    latest_file = None
    latest_date = None
    # Regex to match "US Eye Insurance Guide_MMDDYY.xlsx" and capture MMDDYY
    pattern = re.compile(r"^US Eye Insurance Guide_(\d{6})\.xlsx$")

    for filename in os.listdir(directory):
        match = pattern.match(filename)
        if match:
            date_str = match.group(1)
            try:
                # Assuming dates are MMDDYY. %y handles 20th/21st century.
                file_date = datetime.strptime(date_str, "%m%d%y")
                if latest_date is None or file_date > latest_date:
                    latest_date = file_date
                    latest_file = os.path.join(directory, filename)
            except ValueError:
                print(f"Warning: Found file '{filename}' with a date part ('{date_str}') that could not be parsed. Skipping.")
                continue
    return latest_file, latest_date

def main():
    output_dir = "insurance_docs"
    os.makedirs(output_dir, exist_ok=True)

    # Determine script directory to find Excel files relative to the script
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError: # __file__ is not defined (e.g. interactive interpreter)
        script_dir = os.path.abspath(".")
        print(f"Warning: __file__ not defined, using current working directory for Excel file search: {script_dir}")

    excel_file_path, excel_file_date_obj = find_latest_excel_file(script_dir)

    if not excel_file_path:
        print(f"Error: No Excel file matching the pattern 'US Eye Insurance Guide_MMDDYY.xlsx' found in {script_dir}. Exiting.")
        return 
    else:
        print(f"Using Excel file: {excel_file_path}")
    
    last_updated_text = ""
    if excel_file_date_obj:
        update_date_str = excel_file_date_obj.strftime("%m/%d/%Y")
        excel_filename_for_display = os.path.basename(excel_file_path)
        last_updated_text = f"*Last Updated: {update_date_str} (based on data from Excel file: {excel_filename_for_display})*\n"
    else:
        last_updated_text = "*Last Updated: Date not available*\n"
    
    sheets_to_process = [
        "Center for Sight",
        "Center for Sight-Naples",
        "Lake Eye ",
        "Retina Health Center",
        "SW FL Eye"
    ]
    sheets_with_extra_location_column_behavior = [
        "Center For Sight",
        "SW FL Eye",
        "Center for Sight-Naples"
    ]

    # Data structures for both guides
    doctor_data = defaultdict(lambda: defaultdict(list))
    insurance_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    try:
        xls = pd.ExcelFile(excel_file_path)
    except FileNotFoundError:
        print(f"Error: Excel file '{excel_file_path}' not found. Please ensure it's in the root directory.")
        return
    except Exception as e:
        print(f"Error reading Excel file '{excel_file_path}': {e}")
        return

    print("Processing Excel sheets for data extraction...")
    for sheet_name in xls.sheet_names:
        if sheet_name not in sheets_to_process:
            continue

        location = sheet_name
        print(f"  Processing sheet: {location}")
        
        try:
            df = xls.parse(sheet_name)
        except Exception as e:
            print(f"    Error parsing sheet '{sheet_name}': {e}")
            continue

        if df.empty:
            print(f"    Sheet '{sheet_name}' is empty. Skipping.")
            continue
            
        headers = [str(header).strip('\ufeff').strip() for header in df.columns.tolist()]

        doctor_column_start_index = 3 
        if sheet_name in sheets_with_extra_location_column_behavior:
            if len(headers) > 3 and headers[3].strip() == "Is this plan only accepted at specific practice locations?".strip():
                doctor_column_start_index = 4
        
        if len(headers) <= doctor_column_start_index:
            print(f"    Warning: No doctor columns found in sheet '{sheet_name}' based on start index {doctor_column_start_index}.")
            continue

        doctor_column_names = headers[doctor_column_start_index:]
        # Explicitly filter out the problematic header if it's treated as a doctor name
        problematic_header_text = "is this plan only accepted at specific practice locations?".lower()
        doctor_column_names = [name for name in doctor_column_names if name.strip().lower() != problematic_header_text]
        
        for _, row_series in df.iterrows():
            row_list = [str(cell) for cell in row_series.tolist()]
            
            if not row_list or not any(cell.strip() for cell in row_list if pd.notna(cell)):
                continue
            
            # Normalize plan name whitespace
            raw_plan_name = str(row_list[0]).strip() if len(row_list) > 0 and pd.notna(row_list[0]) else ""
            plan_name = re.sub(r'\s+', ' ', raw_plan_name).strip()
            
            nextgen_name = str(row_list[1]).strip() if len(row_list) > 1 and pd.notna(row_list[1]) else ""
            referral_auth = str(row_list[2]).strip() if len(row_list) > 2 and pd.notna(row_list[2]) else ""
            
            # Populate doctor_data
            for i, doctor_name_header in enumerate(doctor_column_names):
                doctor_name = str(doctor_name_header).strip()
                status_index = i + doctor_column_start_index
                status = str(row_list[status_index]).strip() if len(row_list) > status_index and pd.notna(row_list[status_index]) else ""
                
                if doctor_name and doctor_name.lower() != 'nan':
                    doctor_data[doctor_name][location].append((plan_name, nextgen_name, referral_auth, status))

            # Populate insurance_data
            if plan_name and plan_name.lower() != 'nan':
                for i, doctor_name_header in enumerate(doctor_column_names):
                    doctor_name = str(doctor_name_header).strip()
                    status_index = i + doctor_column_start_index
                    status = str(row_list[status_index]).strip() if len(row_list) > status_index and pd.notna(row_list[status_index]) else ""
                    
                    if doctor_name and doctor_name.lower() != 'nan' and status and status.lower() != 'nan':
                        insurance_data[plan_name][location][doctor_name].append({
                            'nextgen_name': nextgen_name,
                            'referral_auth': referral_auth,
                            'status': status
                        })
    print("Data extraction complete.")

    # --- Generate "Insurance Guide By Provider" ---
    print("Generating Insurance Guide By Provider...")
    summary_doctor_entries = []
    doctor_files_links = []

    for doctor_name_key in sorted(doctor_data.keys()):
        locations_dict = doctor_data[doctor_name_key]
        location_names = list(locations_dict.keys())
        locations_str = ", ".join(sorted(location_names))
        safe_doctor_name = sanitize_filename(doctor_name_key)
        doctor_filename = f"{safe_doctor_name}.md"
        doctor_filepath = os.path.join(output_dir, doctor_filename)
        
        doctor_files_links.append(f"* [{doctor_name_key} ({locations_str})]({output_dir}/{doctor_filename})")
        # Keep this line for future reference, but don't use it in SUMMARY.md
        summary_doctor_entries.append(f"  * [{doctor_name_key}]({output_dir}/{doctor_filename})")

        with open(doctor_filepath, "w", encoding='utf-8') as doc_outfile:
            doc_outfile.write(f"# {doctor_name_key} - Insurance Guide\n\n")
            doc_outfile.write(f"*This page lists insurance participation for {doctor_name_key}.*\n\n")
            doc_outfile.write(f"<details open><summary>Insurance Details for {doctor_name_key} ({locations_str})</summary>\n\n")
            for loc_name in sorted(locations_dict.keys()):
                doc_outfile.write(f"#### {loc_name}\n\n")
                doc_outfile.write("| Insurance Plan Name | NextGen Name | Referral/Auth | Status |\n")
                doc_outfile.write("|--------------------|-------------|--------------|--------|\n")
                for p_name, ng_name, ref_auth, p_status in locations_dict[loc_name]:
                    p_name_esc = p_name.replace("|", "\\|")
                    ng_name_esc = ng_name.replace("|", "\\|")
                    ref_auth_esc = ref_auth.replace("|", "\\|")
                    p_status_esc = p_status.replace("|", "\\|")
                    doc_outfile.write(f"| {p_name_esc} | {ng_name_esc} | {ref_auth_esc} | {p_status_esc} |\n")
                doc_outfile.write("\n")
            doc_outfile.write("</details>\n\n")
    
    provider_guide_md_path = "Insurance_Guide_By_Provider.md"
    with open(provider_guide_md_path, "w", encoding='utf-8') as outfile:
        outfile.write("# Insurance Guide By Provider\n\n")
        outfile.write(last_updated_text + "\n")
        outfile.write("*This guide lists insurance participation by doctor. Click a doctor\'s name to view all insurance info for that doctor, grouped by location/CSV.*\n\n")
        outfile.write("\n".join(doctor_files_links))
        outfile.write("\n\n")
        # Add status legend to provider guide
        outfile.write(generate_status_legend())
    print(f"Generated {provider_guide_md_path}")

    # --- Generate "Insurance Guide By Insurance" ---
    print("Generating Insurance Guide By Insurance...")
    summary_insurance_entries = []
    insurance_files_links = []
    processed_insurances = set()

    for insurance_name_key in sorted(insurance_data.keys()):
        if insurance_name_key in processed_insurances:
            continue
        processed_insurances.add(insurance_name_key)
        
        safe_insurance_name = sanitize_filename(insurance_name_key)
        insurance_filename = f"{safe_insurance_name}.md"
        insurance_filepath = os.path.join(output_dir, insurance_filename)
        
        insurance_files_links.append(f"* [{insurance_name_key}]({output_dir}/{insurance_filename})")
        # Keep this line for future reference, but don't use it in SUMMARY.md
        summary_insurance_entries.append(f"  * [{insurance_name_key}]({output_dir}/{insurance_filename})")

        with open(insurance_filepath, "w", encoding='utf-8') as ins_outfile:
            ins_outfile.write(f"# {insurance_name_key} - Insurance Guide\n\n")
            ins_outfile.write(f"*This page lists providers who accept {insurance_name_key}, grouped by location.*\n\n")
            ins_outfile.write(f"<details open><summary>Provider Details for {insurance_name_key}</summary>\n\n")
            for loc_name in sorted(insurance_data[insurance_name_key].keys()):
                ins_outfile.write(f"## {loc_name}\n\n")
                ins_outfile.write("| Provider | NextGen Name | Referral/Auth | Status |\n")
                ins_outfile.write("|----------|-------------|--------------|--------|\n")
                for doc_name, details_list in sorted(insurance_data[insurance_name_key][loc_name].items()):
                    for details in details_list:
                        doc_name_esc = doc_name.replace("|", "\\|")
                        ng_name_esc = details['nextgen_name'].replace("|", "\\|")
                        ref_auth_esc = details['referral_auth'].replace("|", "\\|")
                        status_esc = details['status'].replace("|", "\\|")
                        ins_outfile.write(f"| {doc_name_esc} | {ng_name_esc} | {ref_auth_esc} | {status_esc} |\n")
                ins_outfile.write("\n")
            ins_outfile.write("</details>\n\n")

    insurance_guide_md_path = "Insurance_Guide_By_Insurance.md"
    with open(insurance_guide_md_path, "w", encoding='utf-8') as outfile:
        outfile.write("# Insurance Guide By Insurance Plan\n\n")
        outfile.write(last_updated_text + "\n")
        outfile.write("*This guide lists insurance participation by insurance plan. Click an insurance plan to view all providers who accept that insurance, grouped by location.*\n\n")
        # Add note about Generic Insurance Protocol
        outfile.write("> **Note:** If you don't see an insurance plan listed below, please refer to the [Generic Insurance Protocol](https://useyecorp.sharepoint.com/RCM/Shared%20Documents/Forms/AllItems.aspx?id=%2FRCM%2FShared%20Documents%2FFinancial%20Clearance%2FFinancial%20Clearance%20Team%20Protocols%2FGeneric%20Insurance%20Protocol%20%2D%20PAC%2C%20Front%20Desk%2C%20and%20Customer%20Service%2Epdf&parent=%2FRCM%2FShared%20Documents%2FFinancial%20Clearance%2FFinancial%20Clearance%20Team%20Protocols&p=true&ga=1) for guidance.\n\n")
        outfile.write("\n".join(insurance_files_links))
        outfile.write("\n\n")
        # Add status legend to insurance guide
        outfile.write(generate_status_legend())
    print(f"Generated {insurance_guide_md_path}")

    # --- Generate FAQ content once and append to both files ---
    print("Generating FAQ section...")
    faq_markdown_content = ""
    faq_sheet_name = "Insurance Directory Overview"
    if faq_sheet_name in xls.sheet_names:
        try:
            full_sheet_df = xls.parse(faq_sheet_name, header=None)
            header_row_index = 18 
            data_start_row_index = 19
            data_end_row_index = 35 

            if full_sheet_df.shape[0] > data_end_row_index and full_sheet_df.shape[1] >= 2:
                faq_headers = full_sheet_df.iloc[header_row_index, 0:2].tolist()
                faq_data_values = full_sheet_df.iloc[data_start_row_index:data_end_row_index + 1, 0:2].values
                faq_df_for_markdown = pd.DataFrame(faq_data_values, columns=faq_headers)
                faq_df_for_markdown.dropna(how='all', inplace=True)
                if not faq_df_for_markdown.empty and faq_df_for_markdown.columns.nlevels == 1 and faq_df_for_markdown.columns[0] is not None:
                    if faq_df_for_markdown.columns[0] in faq_df_for_markdown:
                         faq_df_for_markdown.dropna(subset=[faq_df_for_markdown.columns[0]], inplace=True)
                    elif str(faq_df_for_markdown.columns[0]).lower() == 'nan' and len(faq_df_for_markdown.columns) > 1 and faq_df_for_markdown.columns[1] is not None and faq_df_for_markdown.columns[1] in faq_df_for_markdown:
                         faq_df_for_markdown.dropna(subset=[faq_df_for_markdown.columns[1]], inplace=True)
                
                if not faq_df_for_markdown.empty:
                    faq_markdown_content = "## Insurance FAQ\n\n" + generate_markdown_for_faq(faq_df_for_markdown) + "\n"
                else:
                    print(f"Warning: FAQ data in sheet '{faq_sheet_name}' (range A19:B36) appears to be empty after processing.")
            else:
                print(f"Warning: Sheet '{faq_sheet_name}' does not have enough rows/columns for the specified FAQ range (A19:B36). FAQ section will be skipped.")
        except Exception as e:
            print(f"Error processing FAQ from sheet '{faq_sheet_name}' using specific range: {e}")
    else:
        print(f"Warning: FAQ sheet '{faq_sheet_name}' not found in Excel file. FAQ section will be skipped.")

    if faq_markdown_content:
        with open(provider_guide_md_path, "a", encoding='utf-8') as outfile:
            outfile.write(faq_markdown_content)
        with open(insurance_guide_md_path, "a", encoding='utf-8') as outfile:
            outfile.write(faq_markdown_content)
        print("FAQ section appended to both main guide files.")
    
    # --- Update SUMMARY.md ---
    print("Updating SUMMARY.md...")
    summary_path = "SUMMARY.md"
    provider_guide_title_text = "* [Insurance Guide By Provider](<Insurance_Guide_By_Provider.md>)"
    insurance_guide_title_text = "* [Insurance Guide By Insurance](<Insurance_Guide_By_Insurance.md>)"
    
    new_summary_lines = []
    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f_summary:
            summary_lines = f_summary.readlines()

        temp_summary_lines = []
        i = 0
        while i < len(summary_lines):
            line = summary_lines[i].strip()
            if line == provider_guide_title_text.strip():
                i += 1 
                while i < len(summary_lines) and summary_lines[i].startswith("  * "):
                    i += 1
                continue 
            elif line == insurance_guide_title_text.strip():
                i += 1
                while i < len(summary_lines) and summary_lines[i].startswith("  * "):
                    i += 1
                continue
            temp_summary_lines.append(summary_lines[i])
            i += 1
        new_summary_lines = temp_summary_lines

    if new_summary_lines and not new_summary_lines[-1].endswith('\n'):
        new_summary_lines[-1] += '\n'

    # Only add main guide titles to SUMMARY.md, not individual entries
    new_summary_lines.append(provider_guide_title_text + "\n")
    # Don't add individual doctor entries
    # for entry in summary_doctor_entries:
    #     new_summary_lines.append(entry + "\n")
    
    new_summary_lines.append(insurance_guide_title_text + "\n")
    # Don't add individual insurance entries
    # for entry in summary_insurance_entries:
    #     new_summary_lines.append(entry + "\n")

    with open(summary_path, "w", encoding="utf-8") as f_summary:
        f_summary.writelines(new_summary_lines)
    print(f"SUMMARY.md updated.")
    print("All guides generated successfully.")

if __name__ == "__main__":
    main() 