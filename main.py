#!/usr/bin/env python3
"""
FastAPI server for processing PDF files and extracting piping line numbers.
Uses the PipingLineExtractor from the parent directory.

Usage:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

API Endpoints:
    POST /extract-piping-lines/ - Upload PDF and get piping lines JSON
    GET /health - Health check endpoint
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to sys.path to import PipingLineExtractor
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)

try:
    from process_pdf_to_piping_lines import PipingLineExtractor
except ImportError as e:
    print(f"Error importing PipingLineExtractor: {e}")
    print(f"Parent directory: {parent_dir}")
    print(f"sys.path: {sys.path}")
    raise


# Create FastAPI app
app = FastAPI(
    title="Piping Line Extractor API",
    description=(
        "API for extracting piping line numbers from PDF files using "
        "Google Document AI"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Piping Line Extractor API",
        "description": "Upload PDF files to extract piping line numbers",
        "endpoints": {
            "POST /extract-piping-lines/": "Upload PDF and extract piping lines",
            "GET /health": "Health check",
            "GET /test": "Web test interface",
            "GET /docs": "Interactive API documentation",
            "GET /redoc": "Alternative API documentation",
        },
        "version": "1.0.0",
    }


@app.get("/test", response_class=HTMLResponse)
async def test_interface():
    """Serve the test UI HTML interface."""
    try:
        with open("test_ui.html", "r") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Test interface not found")


@app.get("/health")
async def health_check():
    """Health check endpoint."""

    # Check if required environment variables are set
    required_env_vars = ["GOOGLE_CLOUD_PROJECT_ID", "DOCUMENT_AI_PROCESSOR_ID"]

    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    env_status = "OK" if not missing_vars else f"Missing: {', '.join(missing_vars)}"

    return {
        "status": "healthy",
        "environment_variables": env_status,
        "service": "Piping Line Extractor API",
        "version": "1.0.0",
    }


@app.post("/extract-piping-lines/")
async def extract_piping_lines(file: UploadFile = File(...)):
    """
    Extract piping line numbers from uploaded PDF file.

    Args:
        file: PDF file to process

    Returns:
        JSON response with extracted piping line data in the same format as process_pdf_to_piping_lines.py

    Raises:
        HTTPException: If file processing fails
    """

    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="File must be a PDF (.pdf extension required)"
        )

    # Check file size (optional - adjust limit as needed)
    if file.size and file.size > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(
            status_code=400, detail="File size too large. Maximum size: 50MB"
        )

    # Create temporary file
    temp_file = None
    try:
        # Create temporary file with PDF content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Initialize extractor
        extractor = PipingLineExtractor()

        # Validate environment variables
        if not extractor.validate_environment_variables():
            raise HTTPException(
                status_code=500,
                detail=(
                    "Server configuration error: Missing required environment "
                    "variables for Google Document AI"
                ),
            )

        # Process the PDF file
        print(f"Processing uploaded file: {file.filename} (temp: {temp_file_path})")

        # Extract text and layout from PDF
        document_dict = extractor.process_pdf_with_document_ai(temp_file_path)
        text, layout_info = extractor.extract_text_and_layout_from_document(
            document_dict
        )

        # Extract PID identifier
        pid_identifier = extractor.extract_pid_identifier(text)

        # Extract piping line numbers
        piping_lines_data = extractor.extract_piping_line_numbers(text, layout_info)

        # Filter with validation
        validated_lines_data = {
            line: data
            for line, data in piping_lines_data.items()
            if extractor.validate_piping_line(line)
        }

        # Prepare response in the exact format as process_pdf_to_piping_lines.py
        from datetime import datetime

        result = {
            "metadata": {
                "source_file": file.filename,
                "extraction_timestamp": datetime.now().isoformat(),
                "total_found": len(validated_lines_data),
                "extraction_script": "fastapi_server/main.py",
                "pid_identifier": pid_identifier,
            },
            "piping_lines": [],
        }

        # Convert to the expected format
        for piping_line in sorted(validated_lines_data.keys()):
            line_num, context, coords = validated_lines_data[piping_line]

            entry = {
                "piping_line_number": piping_line,
                "text_line_number": line_num,
                "context": context,
                "coordinates": coords if coords else None,
            }

            result["piping_lines"].append(entry)

        print(
            f"Successfully processed {file.filename}: "
            f"found {len(validated_lines_data)} piping lines"
        )

        return JSONResponse(content=result)

    except Exception as e:
        error_msg = f"Error processing PDF file: {str(e)}"
        print(f"ERROR: {error_msg}")
        print(f"Traceback: {traceback.format_exc()}")

        raise HTTPException(status_code=500, detail=error_msg)

    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                print(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                print(f"Warning: Could not delete temporary file {temp_file_path}: {e}")


@app.get("/extract-piping-lines/")
async def extract_piping_lines_get():
    """
    GET endpoint for extract-piping-lines to show usage information.
    """
    return {
        "message": "Use POST method to upload PDF files",
        "usage": {
            "method": "POST",
            "endpoint": "/extract-piping-lines/",
            "content_type": "multipart/form-data",
            "parameters": {"file": "PDF file to process (required)"},
        },
        "example_curl": (
            "curl -X POST -F 'file=@your_file.pdf' "
            "http://localhost:8000/extract-piping-lines/"
        ),
    }


if __name__ == "__main__":
    import uvicorn

    # Check environment variables on startup
    extractor = PipingLineExtractor()
    if not extractor.validate_environment_variables():
        print(
            "WARNING: Missing required environment variables. "
            "Server will start but requests may fail."
        )
        print("Make sure to run 'source setup_env.sh' before starting the server.")

    print("Starting Piping Line Extractor API server...")
    print("API Documentation available at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("")

    # Use reload=False to avoid the warning when running from main.py
    # For development with reload, use: uvicorn main:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
