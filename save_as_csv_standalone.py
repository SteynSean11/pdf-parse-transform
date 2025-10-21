#!/usr/bin/env python3
"""Standalone utility to convert PDF parsing JSON responses to CSV files"""

import json
import csv
import io
import sys
import os
import re


def save_json_response_as_csv(json_response: dict, output_path: str) -> bool:
    """
    Save the content from a JSON API response as a CSV file

    Args:
        json_response: The JSON response from the PDF parsing API
        output_path: Path where to save the CSV file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Extract content from the response
        content_str = json_response.get("content", "")
        output_format = json_response.get("output_format", "")

        if not content_str:
            print("No content found in JSON response")
            return False

        # If the content is already CSV format, check if it needs to be transformed
        if output_format == "csv":
            # Check if it's the old "Page Number,Content" format that needs parsing
            if content_str.strip().startswith("Page Number,Content"):
                print(
                    "Detected old format CSV with concatenated content - intelligently parsing..."
                )
                return _transform_old_csv_format(content_str, output_path)
            else:
                # It's already in good format, save it directly
                with open(output_path, "w", newline="", encoding="utf-8") as f:
                    f.write(content_str)
                return True

        # If content is JSON, parse it and convert to CSV
        elif output_format == "json":
            import json as json_module

            content_data = json_module.loads(content_str)
            return _save_parsed_content_as_csv(content_data, output_path)

        else:
            print(f"Unsupported output format in response: {output_format}")
            return False

    except Exception as e:
        print(f"Error saving CSV: {str(e)}")
        return False


def _transform_old_csv_format(csv_content: str, output_path: str) -> bool:
    """
    Transforms the old 'Page Number,Content' CSV format into a properly delimited CSV file.
    The Content field contains concatenated purchase rows with single-space separation.
    We use regex to find the pattern: Date + 6 numeric fields, then work backward to extract the item/supplier/ref.
    """
    try:
        output_rows = []
        # Define the expected header for the final, corrected CSV.
        header = [
            "Item",
            "Supplier",
            "Supplier Ref",
            "Date",
            "Qty",
            "Cost",
            "Tax",
            "Total",
            "Paid",
            "Due",
        ]
        output_rows.append(header)

        # Use csv.reader to handle the input CSV string.
        reader = csv.reader(io.StringIO(csv_content))
        next(reader)  # Skip the old header ('Page Number', 'Content').

        full_text_content = []
        for row in reader:
            if len(row) >= 2:
                # The entire page's text is in the second column.
                full_text_content.append(row[1])

        # Join all content into one massive string
        all_text = " ".join(full_text_content)

        # Pattern to match a complete purchase row:
        # Ends with: Date (DD/MM/YYYY) + 6 numeric fields (Qty, Cost, Tax, Total, Paid, Due)
        # The pattern captures: everything before date, date, and 6 numbers
        row_pattern = r"([^0-9]+?)\s+(\d{2}/\d{2}/\d{4})\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)(?=\s+[A-Za-z]|\s*$)"

        matches = re.finditer(row_pattern, all_text)

        for match in matches:
            # Group 1: Item + Supplier + Ref (we need to split this)
            left_text = match.group(1).strip()
            # Groups 2-8: Date, Qty, Cost, Tax, Total, Paid, Due
            date = match.group(2)
            qty = match.group(3)
            cost = match.group(4)
            tax = match.group(5)
            total = match.group(6)
            paid = match.group(7)
            due = match.group(8)

            # Skip header/footer lines
            if any(
                skip in left_text
                for skip in [
                    "Period:",
                    "Selection:",
                    "ALL Item Supplier",
                    "Page",
                    "©",
                    "Pilot Software",
                ]
            ):
                continue

            # Try to intelligently split the left_text into Item, Supplier, Supplier Ref
            # Strategy: Look for patterns like alphanumeric codes (refs) or known supplier names
            parts = left_text.split()

            # Find the supplier ref (usually an alphanumeric code like INV00123456, SBG299, etc.)
            supplier_ref_idx = -1
            for i, part in enumerate(parts):
                if re.match(r"^[A-Z]{2,}[0-9]+|^[0-9]{5,}|^[A-Z]+\d+$", part):
                    supplier_ref_idx = i
                    break

            if supplier_ref_idx >= 2:
                # Everything before ref = Item + Supplier
                item_supplier = parts[:supplier_ref_idx]
                supplier_ref = parts[supplier_ref_idx]

                # Find where supplier starts (look for capitalized words after item)
                supplier_start = 1
                for i in range(1, len(item_supplier)):
                    if item_supplier[i][0].isupper() or item_supplier[i] in [
                        "pick",
                        "oil",
                        "Three",
                    ]:
                        supplier_start = i
                        break

                item = " ".join(item_supplier[:supplier_start])
                supplier = " ".join(item_supplier[supplier_start:])
            else:
                # Couldn't find clear boundaries, use simpler split
                if len(parts) >= 3:
                    item = parts[0]
                    supplier = " ".join(parts[1:-1]) if len(parts) > 2 else parts[1]
                    supplier_ref = parts[-1] if len(parts) > 2 else ""
                else:
                    item = left_text
                    supplier = ""
                    supplier_ref = ""

            output_rows.append(
                [item, supplier, supplier_ref, date, qty, cost, tax, total, paid, due]
            )

        # Write the cleaned and structured rows to the output CSV file.
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(output_rows)

        print(f"Successfully transformed and saved to {output_path}")
        return True

    except Exception as e:
        print(f"Error transforming old CSV format: {e}")
        import traceback

        traceback.print_exc()
        return False


def _save_parsed_content_as_csv(content_data: dict, output_path: str) -> bool:
    """
    Save parsed content data as CSV file

    Args:
        content_data: Parsed content dictionary
        output_path: Path to save CSV file

    Returns:
        True if successful
    """
    try:
        pages = content_data.get("pages", [])

        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)

            # Write header for purchase order data
            writer.writerow(
                [
                    "Item",
                    "Supplier",
                    "Supplier Ref",
                    "Date",
                    "Qty",
                    "Cost",
                    "Tax",
                    "Total",
                    "Paid",
                    "Due",
                ]
            )

            # Write page data
            for page in pages:
                page_num = page.get("page_number", "?")
                text = page.get("text", "").replace("\n", " ").strip()
                has_tables = "Yes" if page.get("has_tables", False) else "No"
                ocr_processed = "Yes" if page.get("ocr_processed", False) else "No"

                writer.writerow([page_num, text, has_tables, ocr_processed])

        return True

    except Exception as e:
        print(f"Error writing CSV: {str(e)}")
        return False


def main():
    """Convert JSON response to CSV"""
    if len(sys.argv) != 3:
        print(
            "Usage: python save_as_csv_standalone.py <input_json_file> <output_csv_file>"
        )
        print("Example: python save_as_csv_standalone.py response.json output.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist")
        sys.exit(1)

    try:
        # Load JSON response
        with open(input_file, "r", encoding="utf-8") as f:
            json_response = json.load(f)

        # Save as CSV
        success = save_json_response_as_csv(json_response, output_file)

        if success:
            print(f"Successfully saved CSV to: {output_file}")
        else:
            print("Failed to save CSV")
            sys.exit(1)

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
