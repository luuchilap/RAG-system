"""
Text extraction utility for various file formats.
Supports PDF, TXT, MD, and DOCX file types.
"""
import os
from typing import Optional
from fastapi import HTTPException


def extract_text_from_file(file_path: str, file_extension: str) -> Optional[str]:
    """
    Extract text from a file based on its extension.
    
    Args:
        file_path: Path to the file
        file_extension: File extension (e.g., '.pdf', '.txt')
    
    Returns:
        Extracted text as a string, or None if extraction fails
    
    Raises:
        HTTPException: If file type is not supported or extraction fails
    """
    file_extension = file_extension.lower()
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="File not found")
    
    try:
        if file_extension == '.pdf':
            return _extract_from_pdf(file_path)
        elif file_extension == '.txt':
            return _extract_from_txt(file_path)
        elif file_extension == '.md':
            return _extract_from_md(file_path)
        elif file_extension == '.docx':
            return _extract_from_docx(file_path)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_extension}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting text from file: {str(e)}"
        )


def _extract_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file using pypdf."""
    try:
        from pypdf import PdfReader
        
        reader = PdfReader(file_path)
        text_parts = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        return "\n\n".join(text_parts)
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="pypdf library is not installed"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading PDF file: {str(e)}"
        )


def _extract_from_txt(file_path: str) -> str:
    """Extract text from a plain text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error reading text file: {str(e)}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading text file: {str(e)}"
        )


def _extract_from_md(file_path: str) -> str:
    """Extract text from a Markdown file."""
    # Markdown files are plain text, so we can use the same method as TXT
    return _extract_from_txt(file_path)


def _extract_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        from docx import Document
        
        doc = Document(file_path)
        text_parts = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        
        return "\n\n".join(text_parts)
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="python-docx library is not installed"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading DOCX file: {str(e)}"
        )

