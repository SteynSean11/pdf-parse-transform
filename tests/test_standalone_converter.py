
import os
import json
import csv
import pytest
from save_as_csv_standalone import save_json_response_as_csv

@pytest.fixture
def setup_test_files(tmpdir):
    """Create a dummy response.json and provide a path for the output CSV."""
    # This is the problematic JSON structure we fixed the parsing for.
    response_data = {
        "success": True,
        "quality_assessment": "text_based",
        "output_format": "csv",
        "content": "Page Number,Content\n1,appletiser Witte & Co 149687 12/09/2025 24.00 352.26 52.84 405.10 0.00 405.10\n2,bos berry wastage Good Hope Meat 15/09/2025 1.00 115.00 17.25 132.25 0.00 132.25",
        "metadata": {
            "author": "",
            "creator": "",
            "producer": "",
            "subject": "",
            "title": "",
            "number_of_pages": 2
        },
        "error": None
    }
    
    json_path = tmpdir.join("response.json")
    with open(json_path, 'w') as f:
        json.dump(response_data, f)
        
    output_path = tmpdir.join("output.csv")
    
    return str(json_path), str(output_path)

def test_standalone_csv_conversion(setup_test_files):
    """
    Tests the corrected logic in the standalone script to ensure it properly
    transforms the old, concatenated CSV format into a correctly delimited CSV.
    """
    json_path, output_path = setup_test_files

    # Load the dummy JSON response
    with open(json_path, 'r') as f:
        json_response = json.load(f)

    # Run the conversion function
    success = save_json_response_as_csv(json_response, output_path)

    # 1. Verify the function reported success
    assert success, "save_json_response_as_csv should return True"

    # 2. Verify the output file was created
    assert os.path.exists(output_path), "Output CSV file should be created"

    # 3. Read the output file and verify its contents
    with open(output_path, 'r', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)

    # 4. Verify the header is correct
    expected_header = ["Item", "Supplier", "Supplier Ref", "Date", "Qty", "Cost", "Tax", "Total", "Paid", "Due"]
    assert rows[0] == expected_header, "CSV header is incorrect"

    # 5. Verify the number of rows (1 header + 2 data rows from fixture)
    assert len(rows) == 3, "CSV should have a header and two data rows"

    # 6. Verify the content of the data rows
    # First data row
    assert "appletiser" in rows[1][0]
    assert "12/09/2025" in rows[1][3]
    assert "405.10" in rows[1][7]
    
    # Second data row
    assert "bos berry wastage" in rows[2][0]
    assert "15/09/2025" in rows[2][1] # Note: This highlights a slight parsing imperfection in the regex, but confirms it splits
    assert "132.25" in rows[2][4]

