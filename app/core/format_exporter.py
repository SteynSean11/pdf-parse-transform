"""Format export module for converting content to various formats"""

import json
import csv
import io
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Dict, Any
from app.models.schemas import ParsedContent, OutputFormat


class FormatExporter:
    """Exports normalized content to various formats"""

    @staticmethod
    def export(
        content: ParsedContent,
        output_format: OutputFormat,
        include_metadata: bool = True,
    ) -> str:
        """
        Export content to specified format

        Args:
            content: Normalized parsed content
            output_format: Target format
            include_metadata: Whether to include metadata

        Returns:
            Formatted content as string
        """
        if output_format == OutputFormat.PLAIN_TEXT:
            return FormatExporter._export_plain_text(content)
        elif output_format == OutputFormat.MARKDOWN:
            return FormatExporter._export_markdown(content, include_metadata)
        elif output_format == OutputFormat.CSV:
            return FormatExporter._export_csv(content)
        elif output_format == OutputFormat.XML:
            return FormatExporter._export_xml(content, include_metadata)
        elif output_format == OutputFormat.JSON:
            return FormatExporter._export_json(content, include_metadata)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    @staticmethod
    def _export_plain_text(content: ParsedContent) -> str:
        """Export as plain text"""
        return content.text_content

    @staticmethod
    def _export_markdown(content: ParsedContent, include_metadata: bool) -> str:
        """Export as markdown"""
        lines = []

        # Add title if available
        if content.title:
            lines.append(f"# {content.title}\n")

        # Add metadata section
        if include_metadata and content.metadata:
            lines.append("## Metadata\n")
            for key, value in content.metadata.items():
                lines.append(f"- **{key}**: {value}")
            lines.append("")

        # Add content by page
        lines.append("## Content\n")
        for page in content.pages:
            page_num = page.get("page_number", "?")
            lines.append(f"### Page {page_num}\n")
            lines.append(page.get("text", ""))
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _export_csv(content: ParsedContent) -> str:
        """Export as CSV (table-based if tables detected, otherwise page-based)"""
        # Check if any pages have tables
        has_tables = any(page.get("has_tables", False) for page in content.pages)

        if has_tables:
            return FormatExporter._export_csv_from_tables(content)
        else:
            return FormatExporter._export_csv_page_based(content)

    @staticmethod
    def _export_csv_page_based(content: ParsedContent) -> str:
        """Export as CSV by attempting to parse structured text data from pages"""
        import re

        output = io.StringIO()
        writer = csv.writer(output)

        # Write header row
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

        # Collect all structured data from pages
        for page in content.pages:
            text = page.get("text", "")
            if not text.strip():
                continue

            # Split by newlines - preserve line structure
            lines = [line.strip() for line in text.split("\n") if line.strip()]

            # Analyze lines to detect columns
            parsed_rows = FormatExporter._parse_text_to_rows(lines)

            if parsed_rows:
                writer.writerows(parsed_rows)

        return output.getvalue()

    @staticmethod
    def _parse_text_to_rows(lines: list) -> list:
        """Parse text lines into structured CSV rows by splitting on multiple spaces"""
        import re

        if not lines:
            return []

        # Filter out footer/header lines and empty lines
        meaningful_lines = [
            line.strip()
            for line in lines
            if line.strip()
            and not re.match(
                r"^(Page \d+|^|\s+©|.*\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})", line
            )
        ]

        if not meaningful_lines:
            return []

        rows = []

        # Simple approach: split lines on runs of 2 or more spaces
        for line in meaningful_lines:
            if len(line.strip()) > 0:
                # Split on 2+ spaces
                fields = re.split(r"  +", line.strip())
                if len(fields) > 1:
                    rows.append([f.strip() for f in fields if f.strip()])
                else:
                    # Single field, still add it
                    rows.append([line.strip()])

        return rows

    @staticmethod
    def _detect_column_positions(lines: list) -> list:
        """Detect column start positions by analyzing space patterns"""
        if not lines:
            return []

        # Find positions where multiple spaces appear (column separators)
        # We look for gaps of 2+ spaces that appear consistently across lines
        gap_positions = {}  # position -> count

        for line in lines:
            i = 0
            while i < len(line):
                # Look for runs of 2+ spaces
                if i < len(line) and line[i] == " ":
                    space_start = i
                    space_count = 0
                    while i < len(line) and line[i] == " ":
                        space_count += 1
                        i += 1

                    # If it's a multi-space gap, record the position where it starts
                    if space_count >= 2:
                        if space_start not in gap_positions:
                            gap_positions[space_start] = 0
                        gap_positions[space_start] += 1
                else:
                    i += 1

        # Sort by frequency (most common gaps first)
        sorted_gaps = sorted(gap_positions.items(), key=lambda x: (-x[1], x[0]))

        # Keep gaps that appear in at least 30% of lines
        threshold = max(1, len(lines) * 0.3)
        positions = [pos for pos, count in sorted_gaps if count >= threshold]

        return sorted(positions) if positions else []

    @staticmethod
    def _split_by_positions(line: str, positions: list) -> list:
        """Split a line by detected multi-space column positions"""
        if not positions or not line:
            return [line.strip()] if line.strip() else []

        row = []
        start = 0

        for gap_pos in positions:
            if start < gap_pos and start < len(line):
                # Extract text from current position to gap position
                field = line[start:gap_pos].strip()
                if field:
                    row.append(field)
            # Move start to after the gap (skip spaces)
            start = gap_pos
            while start < len(line) and line[start] == " ":
                start += 1

        # Add remaining text
        if start < len(line):
            field = line[start:].strip()
            if field:
                row.append(field)

        return row if row else []

    @staticmethod
    def _export_csv_from_tables(content: ParsedContent) -> str:
        """Export as CSV from extracted tables"""
        output = io.StringIO()
        writer = csv.writer(output)

        # Collect all table data
        headers_written = False

        for page in content.pages:
            tables = page.get("tables", [])
            for table in tables:
                if not table:
                    continue

                # Assume first row is headers if we haven't written headers yet
                if not headers_written and len(table) > 0:
                    # Clean and write headers
                    headers = [
                        str(cell).strip()
                        for cell in table[0]
                        if cell and str(cell).strip()
                    ]
                    if headers:
                        writer.writerow(headers)
                        headers_written = True
                        # Skip the header row from data
                        data_rows = table[1:] if len(table) > 1 else []
                    else:
                        data_rows = table
                else:
                    data_rows = table

                # Write data rows
                for row in data_rows:
                    if row:  # Skip empty rows
                        # Clean the row data
                        clean_row = []
                        for cell in row:
                            # Convert to string and clean
                            cell_str = str(cell).strip() if cell is not None else ""
                            clean_row.append(cell_str)
                        if any(clean_row):  # Only write non-empty rows
                            writer.writerow(clean_row)

        # If no tables had headers, add a default header
        if not headers_written:
            writer.writerow(
                [
                    "Column 1",
                    "Column 2",
                    "Column 3",
                    "Column 4",
                    "Column 5",
                    "Column 6",
                    "Column 7",
                    "Column 8",
                    "Column 9",
                    "Column 10",
                ]
            )

        return output.getvalue()

    @staticmethod
    def _export_xml(content: ParsedContent, include_metadata: bool) -> str:
        """Export as XML"""
        root = ET.Element("document")

        # Add title
        if content.title:
            title_elem = ET.SubElement(root, "title")
            title_elem.text = content.title

        # Add metadata
        if include_metadata and content.metadata:
            metadata_elem = ET.SubElement(root, "metadata")
            for key, value in content.metadata.items():
                meta_item = ET.SubElement(metadata_elem, "item", name=key)
                meta_item.text = str(value)

        # Add pages
        pages_elem = ET.SubElement(root, "pages", count=str(content.page_count))
        for page in content.pages:
            page_elem = ET.SubElement(
                pages_elem, "page", number=str(page.get("page_number", "?"))
            )
            text_elem = ET.SubElement(page_elem, "text")
            text_elem.text = page.get("text", "")

            # Add additional page attributes
            if page.get("has_tables"):
                page_elem.set("has_tables", "true")
            if page.get("ocr_processed"):
                page_elem.set("ocr_processed", "true")

        # Pretty print XML
        xml_str = ET.tostring(root, encoding="unicode")
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent="  ")

    @staticmethod
    def _export_json(content: ParsedContent, include_metadata: bool) -> str:
        """Export as JSON"""
        data = {
            "page_count": content.page_count,
            "text_content": content.text_content,
            "pages": content.pages,
        }

        if content.title:
            data["title"] = content.title

        if include_metadata:
            data["metadata"] = content.metadata

        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def save_json_response_as_csv(
        json_response: Dict[str, Any], output_path: str
    ) -> bool:
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

            # If the content is already CSV format, save it directly
            if output_format == "csv":
                with open(output_path, "w", newline="", encoding="utf-8") as f:
                    f.write(content_str)
                return True

            # If content is JSON, parse it and convert to CSV
            elif output_format == "json":
                content_data = json.loads(content_str)
                return FormatExporter._save_parsed_content_as_csv(
                    content_data, output_path
                )

            else:
                print(f"Unsupported output format in response: {output_format}")
                return False

        except Exception as e:
            print(f"Error saving CSV: {str(e)}")
            return False

    @staticmethod
    def _save_parsed_content_as_csv(
        content_data: Dict[str, Any], output_path: str
    ) -> bool:
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

                # Write header
                writer.writerow(
                    ["Page Number", "Content", "Has Tables", "OCR Processed"]
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
