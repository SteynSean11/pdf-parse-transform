"""Content normalization module"""
from app.models.schemas import ParsedContent


class ContentNormalizer:
    """Normalizes parsed content into standard structure"""
    
    @staticmethod
    def normalize(content: ParsedContent) -> ParsedContent:
        """
        Normalize and clean parsed content
        
        Args:
            content: Raw parsed content
            
        Returns:
            Normalized ParsedContent
        """
        # Clean up text content
        text_lines = content.text_content.split("\n")
        cleaned_lines = [line.strip() for line in text_lines if line.strip()]
        normalized_text = "\n".join(cleaned_lines)
        
        # Update pages with normalized text
        normalized_pages = []
        for page in content.pages:
            normalized_page = page.copy()
            if "text" in normalized_page:
                page_lines = normalized_page["text"].split("\n")
                cleaned_page_lines = [line.strip() for line in page_lines if line.strip()]
                normalized_page["text"] = "\n".join(cleaned_page_lines)
            normalized_pages.append(normalized_page)
        
        return ParsedContent(
            title=content.title,
            pages=normalized_pages,
            metadata=content.metadata,
            text_content=normalized_text,
            page_count=content.page_count
        )
