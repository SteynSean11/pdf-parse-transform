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
    def export(content: ParsedContent, output_format: OutputFormat, include_metadata: bool = True) -> str:
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
        """Export as CSV (page-based)"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["Page Number", "Content"])
        
        # Write page data
        for page in content.pages:
            page_num = page.get("page_number", "?")
            text = page.get("text", "").replace("\n", " ")
            writer.writerow([page_num, text])
        
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
            page_elem = ET.SubElement(pages_elem, "page", number=str(page.get("page_number", "?")))
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
            "pages": content.pages
        }
        
        if content.title:
            data["title"] = content.title
        
        if include_metadata:
            data["metadata"] = content.metadata
        
        return json.dumps(data, indent=2, ensure_ascii=False)
