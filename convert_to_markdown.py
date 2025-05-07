import csv
import os
import glob

def csv_to_markdown_table(csv_file):
    """Convert a CSV file to a Markdown table."""
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        # Create the header row
        markdown = "| " + " | ".join(headers) + " |\n"
        # Create the separator row
        markdown += "| " + " | ".join(["---"] * len(headers)) + " |\n"
        
        # Add the data rows
        for row in reader:
            # Clean and escape any pipe characters in the data
            cleaned_row = [str(cell).replace("|", "\\|") for cell in row]
            markdown += "| " + " | ".join(cleaned_row) + " |\n"
            
        return markdown

def main():
    # Get all CSV files except those with Zone.Identifier
    csv_files = [f for f in glob.glob("*.csv") if not f.endswith("Zone.Identifier")]
    
    # Create the output file
    with open("Insurance_Guide.md", "w", encoding="utf-8") as outfile:
        # Add a title
        outfile.write("# Insurance Guide\n\n")
        
        # First, process Insurance_FAQ.csv if it exists
        if "Insurance_FAQ.csv" in csv_files:
            outfile.write("## Insurance FAQ\n\n")
            markdown_table = csv_to_markdown_table("Insurance_FAQ.csv")
            outfile.write(markdown_table)
            outfile.write("\n\n")
            csv_files.remove("Insurance_FAQ.csv")
        
        # Sort remaining files alphabetically
        csv_files.sort()
        
        # Process remaining CSV files
        for csv_file in csv_files:
            # Add a section header with the file name (without extension)
            section_name = os.path.splitext(csv_file)[0]
            outfile.write(f"## {section_name}\n\n")
            
            # Convert and write the table
            markdown_table = csv_to_markdown_table(csv_file)
            outfile.write(markdown_table)
            outfile.write("\n\n")  # Add some spacing between tables

if __name__ == "__main__":
    main() 