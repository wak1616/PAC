import pandas as pd
import os
from collections import defaultdict
import re
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("insurance_guide_generation.log"),
        logging.StreamHandler()
    ]
)

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

def find_excel_file(directory):
    """
    Finds the Excel file in the given directory that matches the name
    "US Eye Insurance Guide.xlsx".
    """
    filename = "US Eye Insurance Guide.xlsx"
    file_path = os.path.join(directory, filename)
    
    if os.path.exists(file_path):
        return file_path
    else:
        return None

def detect_column_structure(df, sheet_name):
    """Detect column structure and identify doctor columns correctly"""
    headers = [str(col).strip('\ufeff').strip() for col in df.columns.tolist()]
    logging.info(f"Headers in sheet '{sheet_name}': {headers}")
    
    # Base columns should always be present 
    insurance_col_idx = 0
    nextgen_col_idx = 1
    referral_col_idx = 2
    
    # Special column check
    doctor_column_start_idx = 3  # Default 
    special_col_text = "Is this plan only accepted at specific practice locations?".lower().strip()
    
    # Look for the location column in any position
    for i, header in enumerate(headers):
        if i >= 3 and header.lower().strip() == special_col_text:
            doctor_column_start_idx = i + 1
            logging.info(f"Found location-specific column at position {i}, doctors start at {doctor_column_start_idx}")
            break
    
    # List all doctor column names
    doctor_column_names = headers[doctor_column_start_idx:]
    
    # Filter out columns that are not actual doctor names (might be empty or contain misleading text)
    doctor_column_names = [name for name in doctor_column_names 
                         if name and name.strip() and name.lower() != 'nan' and special_col_text not in name.lower()]
    
    logging.info(f"Detected {len(doctor_column_names)} doctor columns in sheet '{sheet_name}': {doctor_column_names}")
    
    return {
        'insurance_col_idx': insurance_col_idx,
        'nextgen_col_idx': nextgen_col_idx,
        'referral_col_idx': referral_col_idx,
        'doctor_column_start_idx': doctor_column_start_idx,
        'doctor_column_names': doctor_column_names,
        'headers': headers
    }

def main():
    output_dir = "insurance_docs"
    os.makedirs(output_dir, exist_ok=True)

    # Determine script directory to find Excel files relative to the script
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError: # __file__ is not defined (e.g. interactive interpreter)
        script_dir = os.path.abspath(".")
        logging.warning(f"__file__ not defined, using current working directory for Excel file search: {script_dir}")

    excel_file_path = find_excel_file(script_dir)

    if not excel_file_path:
        logging.error(f"No Excel file named 'US Eye Insurance Guide.xlsx' found in {script_dir}. Exiting.")
        return 
    else:
        logging.info(f"Using Excel file: {excel_file_path}")
    
    # Get the modification date of the Excel file for the last updated text
    last_updated_text = ""
    try:
        excel_mod_time = os.path.getmtime(excel_file_path)
        excel_mod_date = datetime.fromtimestamp(excel_mod_time)
        update_date_str = excel_mod_date.strftime("%m/%d/%Y")
        excel_filename_for_display = os.path.basename(excel_file_path)
        last_updated_text = f"*Last Updated: {update_date_str} (based on data from Excel file: {excel_filename_for_display})*\n"
    except Exception as e:
        logging.warning(f"Could not get modification date for Excel file: {e}")
        last_updated_text = "*Last Updated: Date not available*\n"
    
    # Normalize sheet names to handle trailing/leading spaces
    sheets_to_process = [
        "Center for Sight",
        "Center for Sight-Naples",
        "Lake Eye",  # Will match with any variations of leading/trailing spaces
        "Retina Health Center",
        "SW FL Eye"
    ]

    # Data structures for both guides
    doctor_data = defaultdict(lambda: defaultdict(list))
    insurance_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    try:
        xls = pd.ExcelFile(excel_file_path)
    except FileNotFoundError:
        logging.error(f"Excel file '{excel_file_path}' not found. Please ensure it's in the root directory.")
        return
    except Exception as e:
        logging.error(f"Error reading Excel file '{excel_file_path}': {e}")
        return

    # Debugging: Print all sheet names to verify
    logging.info(f"Excel sheets available: {xls.sheet_names}")
    
    logging.info("Processing Excel sheets for data extraction...")
    
    # Track if any problems were encountered
    data_issues = []
    
    for sheet_name in xls.sheet_names:
        # Normalize sheet name for comparison
        normalized_sheet_name = sheet_name.strip()
        
        if normalized_sheet_name not in sheets_to_process:
            # Check if any sheet name matches after stripping spaces
            sheet_match = False
            for process_sheet in sheets_to_process:
                if normalized_sheet_name.strip() == process_sheet.strip():
                    sheet_match = True
                    break
            
            if not sheet_match:
                continue

        location = sheet_name
        logging.info(f"Processing sheet: {location}")
        
        try:
            df = xls.parse(sheet_name)
        except Exception as e:
            logging.error(f"Error parsing sheet '{sheet_name}': {e}")
            data_issues.append(f"Could not parse sheet '{sheet_name}': {e}")
            continue

        if df.empty:
            logging.warning(f"Sheet '{sheet_name}' is empty. Skipping.")
            continue
        
        # Detect column structure for this sheet
        column_info = detect_column_structure(df, sheet_name)
        
        if not column_info['doctor_column_names']:
            logging.warning(f"No doctor columns detected in sheet '{sheet_name}'. Skipping.")
            data_issues.append(f"No doctor columns found in sheet '{sheet_name}'")
            continue
            
        doctor_column_start_idx = column_info['doctor_column_start_idx']
        doctor_column_names = column_info['doctor_column_names']
        headers = column_info['headers']
        
        # Process rows
        processed_rows = 0
        for _, row_series in df.iterrows():
            row_list = row_series.tolist()
            
            if not row_list or not any(cell.strip() for cell in map(str, row_list) if pd.notna(cell)):
                continue
            
            processed_rows += 1
            
            # Normalize plan name whitespace
            raw_plan_name = str(row_list[column_info['insurance_col_idx']]).strip() if len(row_list) > column_info['insurance_col_idx'] and pd.notna(row_list[column_info['insurance_col_idx']]) else ""
            plan_name = re.sub(r'\s+', ' ', raw_plan_name).strip()
            
            if not plan_name or plan_name.lower() == 'nan':
                continue  # Skip rows without a valid insurance plan name
            
            nextgen_name = str(row_list[column_info['nextgen_col_idx']]).strip() if len(row_list) > column_info['nextgen_col_idx'] and pd.notna(row_list[column_info['nextgen_col_idx']]) else ""
            referral_auth = str(row_list[column_info['referral_col_idx']]).strip() if len(row_list) > column_info['referral_col_idx'] and pd.notna(row_list[column_info['referral_col_idx']]) else ""
            
            # Populate doctor_data and insurance_data
            for i, doctor_name in enumerate(doctor_column_names):
                doctor_idx = doctor_column_start_idx + i
                status = ""
                
                # Verify doctor index is valid
                if doctor_idx < len(row_list):
                    raw_status = row_list[doctor_idx]
                    if pd.notna(raw_status):
                        status = str(raw_status).strip()
                else:
                    # If index is out of range, log the issue
                    logging.warning(f"Doctor index {doctor_idx} out of range for row with plan '{plan_name}' in sheet '{sheet_name}'")
                    data_issues.append(f"Data alignment issue in sheet '{sheet_name}', plan '{plan_name}': doctor column index out of range")
                    continue
                
                if doctor_name and status:
                    # Debug for problematic rows
                    if "Joaquin De Rojas" in doctor_name and "Aetna" in plan_name:
                        logging.info(f"DEBUG: Adding for {doctor_name} with plan {plan_name} - Status: {status}")
                    
                    # Add to doctor data
                    doctor_data[doctor_name][location].append((plan_name, nextgen_name, referral_auth, status))
                    
                    # Add to insurance data 
                    insurance_data[plan_name][location][doctor_name].append({
                        'nextgen_name': nextgen_name,
                        'referral_auth': referral_auth,
                        'status': status
                    })
        
        logging.info(f"Processed {processed_rows} rows in sheet '{sheet_name}'")
    
    if data_issues:
        logging.warning("The following data issues were detected during processing:")
        for issue in data_issues:
            logging.warning(f"  - {issue}")
    
    logging.info("Data extraction complete.")

    # --- Generate "Insurance Guide By Provider" ---
    logging.info("Generating Insurance Guide By Provider...")
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
    logging.info(f"Generated {provider_guide_md_path}")

    # --- Generate "Insurance Guide By Insurance" ---
    logging.info("Generating Insurance Guide By Insurance...")
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
    logging.info(f"Generated {insurance_guide_md_path}")

    # --- Generate FAQ content once and append to both files ---
    logging.info("Generating FAQ section...")
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
                    logging.warning(f"FAQ data in sheet '{faq_sheet_name}' (range A19:B36) appears to be empty after processing.")
            else:
                logging.warning(f"Sheet '{faq_sheet_name}' does not have enough rows/columns for the specified FAQ range (A19:B36). FAQ section will be skipped.")
        except Exception as e:
            logging.error(f"Error processing FAQ from sheet '{faq_sheet_name}' using specific range: {e}")
    else:
        logging.warning(f"FAQ sheet '{faq_sheet_name}' not found in Excel file. FAQ section will be skipped.")

    if faq_markdown_content:
        with open(provider_guide_md_path, "a", encoding='utf-8') as outfile:
            outfile.write(faq_markdown_content)
        with open(insurance_guide_md_path, "a", encoding='utf-8') as outfile:
            outfile.write(faq_markdown_content)
        logging.info("FAQ section appended to both main guide files.")
    
    # --- Update SUMMARY.md ---
    logging.info("Updating SUMMARY.md...")
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
    new_summary_lines.append(insurance_guide_title_text + "\n")

    with open(summary_path, "w", encoding="utf-8") as f_summary:
        f_summary.writelines(new_summary_lines)
    logging.info(f"SUMMARY.md updated.")
    
    # Report any data issues at the end
    if data_issues:
        logging.warning("Some data issues were encountered during processing. Please review the log file for details.")
    else:
        logging.info("All guides generated successfully with no detected data issues.")

if __name__ == "__main__":
    main() 