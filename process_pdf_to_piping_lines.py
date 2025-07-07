#!/usr/bin/env python3
"""
Combined script to process PDF files with Google Document AI and extract piping line numbers.
Takes a PDF file as input and outputs piping line numbers in JSON format.

Usage:
    python process_pdf_to_piping_lines.py input.pdf
    python process_pdf_to_piping_lines.py input.pdf output.json
"""

import os
import sys
import json
import re
from datetime import datetime
from typing import Dict, Tuple, List, Optional

# Google Cloud Document AI imports
from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from google.oauth2 import service_account
from google.protobuf.json_format import MessageToDict


class PipingLineExtractor:
    """Combined PDF processor and piping line extractor."""

    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "eu")
        self.processor_id = os.getenv("DOCUMENT_AI_PROCESSOR_ID")
        self.service_account_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    def validate_environment_variables(self) -> bool:
        """Validate that all required environment variables are set."""
        required_vars = {
            "GOOGLE_CLOUD_PROJECT_ID": self.project_id,
            "DOCUMENT_AI_PROCESSOR_ID": self.processor_id,
        }

        missing_vars = []
        for var_name, var_value in required_vars.items():
            if not var_value:
                missing_vars.append(var_name)

        if missing_vars:
            print("ERROR: Missing required environment variables:")
            for var in missing_vars:
                print(f"  - {var}")
            print("\nPlease set these environment variables before running the script.")
            print("Example:")
            print("  export GOOGLE_CLOUD_PROJECT_ID='your-project-id'")
            print("  export DOCUMENT_AI_PROCESSOR_ID='your-processor-id'")
            print(
                "  export GOOGLE_APPLICATION_CREDENTIALS='path/to/service-account-key.json'  # Optional"
            )
            print("  export GOOGLE_CLOUD_LOCATION='us'  # Optional, defaults to eu")
            return False

        return True

    def get_client(self):
        """Initialize Document AI client with credentials."""
        # Option 1: Use service account credentials from environment variables
        if all(
            [
                os.getenv("GOOGLE_SERVICE_ACCOUNT_TYPE"),
                os.getenv("GOOGLE_SERVICE_ACCOUNT_PROJECT_ID"),
                os.getenv("GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID"),
                os.getenv("GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY"),
                os.getenv("GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL"),
                os.getenv("GOOGLE_SERVICE_ACCOUNT_CLIENT_ID"),
                os.getenv("GOOGLE_SERVICE_ACCOUNT_AUTH_URI"),
                os.getenv("GOOGLE_SERVICE_ACCOUNT_TOKEN_URI"),
            ]
        ):
            try:
                # Fix private key formatting - handle different newline representations
                raw_private_key = os.getenv("GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY")
                private_key = raw_private_key.replace("\\n", "\n")

                # Additional cleaning - sometimes keys have extra quotes or escaping
                if private_key.startswith('"') and private_key.endswith('"'):
                    private_key = private_key[1:-1]

                service_account_info = {
                    "type": os.getenv("GOOGLE_SERVICE_ACCOUNT_TYPE"),
                    "project_id": os.getenv("GOOGLE_SERVICE_ACCOUNT_PROJECT_ID"),
                    "private_key_id": os.getenv(
                        "GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID"
                    ),
                    "private_key": private_key,
                    "client_email": os.getenv("GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL"),
                    "client_id": os.getenv("GOOGLE_SERVICE_ACCOUNT_CLIENT_ID"),
                    "auth_uri": os.getenv("GOOGLE_SERVICE_ACCOUNT_AUTH_URI"),
                    "token_uri": os.getenv("GOOGLE_SERVICE_ACCOUNT_TOKEN_URI"),
                    "auth_provider_x509_cert_url": os.getenv(
                        "GOOGLE_SERVICE_ACCOUNT_AUTH_PROVIDER_X509_CERT_URL"
                    ),
                    "client_x509_cert_url": os.getenv(
                        "GOOGLE_SERVICE_ACCOUNT_CLIENT_X509_CERT_URL"
                    ),
                }

                credentials = service_account.Credentials.from_service_account_info(
                    service_account_info
                )
                return documentai.DocumentProcessorServiceClient(
                    credentials=credentials,
                    client_options=ClientOptions(
                        api_endpoint=f"{self.location}-documentai.googleapis.com"
                    ),
                )
            except Exception as e:
                print(f"Error creating credentials from environment variables: {e}")
                print("Falling back to other authentication methods...")

        # Option 2: Use service account key file (fallback)
        elif self.service_account_file and os.path.exists(self.service_account_file):
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_file
            )
            return documentai.DocumentProcessorServiceClient(
                credentials=credentials,
                client_options=ClientOptions(
                    api_endpoint=f"{self.location}-documentai.googleapis.com"
                ),
            )

        # Option 3: Use Application Default Credentials
        return documentai.DocumentProcessorServiceClient(
            client_options=ClientOptions(
                api_endpoint=f"{self.location}-documentai.googleapis.com"
            )
        )

    def process_pdf_with_document_ai(self, pdf_path: str) -> Dict:
        """Process PDF file with Google Document AI and return document object."""
        print(f"Processing PDF with Document AI: {pdf_path}")
        print(f"Using configuration:")
        print(f"  Project ID: {self.project_id}")
        print(f"  Location: {self.location}")
        print(f"  Processor ID: {self.processor_id}")

        # Get Document AI client
        docai_client = self.get_client()

        # The full resource name of the processor
        name = docai_client.processor_path(
            self.project_id, self.location, self.processor_id
        )

        # Read the PDF file
        with open(pdf_path, "rb") as pdf_file:
            pdf_content = pdf_file.read()

        # Load Binary Data into Document AI RawDocument Object
        raw_document = documentai.RawDocument(
            content=pdf_content, mime_type="application/pdf"
        )

        # Configure the process request
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)

        # Process the document
        result = docai_client.process_document(request=request)

        print("Document AI processing complete.")

        # Convert protobuf to dictionary
        document_dict = MessageToDict(result.document._pb)
        return document_dict

    def extract_text_and_layout_from_document(
        self, document_dict: Dict
    ) -> Tuple[str, List[Dict]]:
        """Extract text content and layout info from Document AI result."""
        text = ""
        layout_info = []

        if "text" in document_dict:
            text = document_dict["text"]
        else:
            print("Warning: No 'text' field found in document")

        # Extract layout information for coordinate mapping
        if "pages" in document_dict:
            for page in document_dict["pages"]:
                if "tokens" in page:
                    for token in page["tokens"]:
                        if "layout" in token and "textAnchor" in token["layout"]:
                            text_anchor = token["layout"]["textAnchor"]
                            if "textSegments" in text_anchor:
                                for segment in text_anchor["textSegments"]:
                                    start_idx = int(segment.get("startIndex", 0))
                                    end_idx = int(segment.get("endIndex", 0))

                                    # Get bounding box coordinates
                                    bbox = None
                                    if "boundingPoly" in token["layout"]:
                                        vertices = token["layout"]["boundingPoly"].get(
                                            "vertices", []
                                        )
                                        if vertices:
                                            bbox = {
                                                "x": vertices[0].get("x", 0),
                                                "y": vertices[0].get("y", 0),
                                                "width": vertices[2].get("x", 0)
                                                - vertices[0].get("x", 0),
                                                "height": vertices[2].get("y", 0)
                                                - vertices[0].get("y", 0),
                                            }

                                    layout_info.append(
                                        {
                                            "start": start_idx,
                                            "end": end_idx,
                                            "bbox": bbox,
                                            "text": (
                                                text[start_idx:end_idx]
                                                if end_idx <= len(text)
                                                else ""
                                            ),
                                        }
                                    )

        return text, layout_info

    def find_coordinates_for_text(
        self, target_text: str, text: str, layout_info: List[Dict]
    ) -> Dict:
        """Find coordinates for specific text in the document."""
        text_upper = text.upper()
        target_upper = target_text.upper()

        start_pos = text_upper.find(target_upper)
        if start_pos == -1:
            return None

        end_pos = start_pos + len(target_text)

        # Find layout info that overlaps with this text position
        for layout in layout_info:
            if (
                layout["start"] <= start_pos < layout["end"]
                or layout["start"] < end_pos <= layout["end"]
                or start_pos <= layout["start"] < end_pos
            ):
                if layout["bbox"]:
                    return layout["bbox"]

        return None

    def extract_piping_line_numbers(
        self, text: str, layout_info: List[Dict]
    ) -> Dict[str, Tuple[int, str, Dict]]:
        """Extract piping line numbers from text using regex patterns."""
        piping_lines = {}
        lines = text.split("\n")

        # Pattern 1: Full format with size and inch mark (4 components)
        pattern1 = r'\b\d{1,2}"-[A-Z]{1,3}-[A-Z0-9]{1,3}-[A-Z0-9]{1,4}\b'

        # Pattern 2: Format with size but no quotes (4 components)
        pattern2 = r"\b\d{1,2}-[A-Z]{1,3}-[A-Z0-9]{1,3}-[A-Z0-9]{1,4}\b"

        # Pattern 3: General 4-component pattern (allowing mixed alphanumeric)
        pattern3 = r'\b[A-Z0-9"]{1,4}-[A-Z]{1,3}-[A-Z0-9]{1,3}-[A-Z0-9]{1,4}\b'

        patterns = [pattern1, pattern2, pattern3]

        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                for match in matches:
                    cleaned_match = match.strip().upper()

                    # Additional validation - must contain at least one dash and some letters
                    if "-" in cleaned_match and re.search(r"[A-Z]", cleaned_match):
                        normalized_match = self.normalize_piping_line(cleaned_match)

                        # Store with line number, context, and coordinates
                        context = line.strip()[:100]  # First 100 chars of line
                        coords = self.find_coordinates_for_text(
                            match, text, layout_info
                        )

                        if normalized_match not in piping_lines:
                            piping_lines[normalized_match] = (line_num, context, coords)

        return piping_lines

    def normalize_piping_line(self, line: str) -> str:
        """Normalize piping line by adding missing quote mark to first component."""
        components = line.split("-")

        if len(components) >= 1:
            first_component = components[0]
            # If first component contains only digits (no quote mark), add quote
            if re.match(r"^\d+$", first_component):
                components[0] = first_component + '"'
                return "-".join(components)

        return line

    def validate_piping_line(self, line: str) -> bool:
        """Additional validation for extracted piping lines."""
        components = line.split("-")

        # Must have exactly 4 components
        if len(components) != 4:
            return False

        # Must contain at least one letter
        if not re.search(r"[A-Z]", line):
            return False

        # Must contain at least one number
        if not re.search(r"\d", line):
            return False

        # Should not be too long or too short
        if len(line) > 20 or len(line) < 7:
            return False

        # First component should contain a number (size) and optionally "
        first_component = components[0]
        if not re.search(r"\d", first_component):
            return False

        # Last component should be alphanumeric
        last_component = components[3]
        if not re.match(r"^[A-Z0-9]+$", last_component):
            return False

        return True

    def extract_pid_identifier(self, text: str) -> Optional[str]:
        """Extract PID identifier from text."""
        # Pattern to match "DWG. NO." followed by PID identifier
        pattern = r"DWG\.\s*NO\.?\s*([A-Z0-9\-]+PID[A-Z0-9\-]*)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Alternative pattern without period after NO
        pattern2 = r"DWG\s*NO\.?\s*([A-Z0-9\-]+PID[A-Z0-9\-]*)"
        match2 = re.search(pattern2, text, re.IGNORECASE)
        if match2:
            return match2.group(1).strip()

        return None

    def save_results_as_json(
        self,
        piping_lines_data: Dict[str, Tuple[int, str, Dict]],
        pdf_file: str,
        output_file: str,
        pid_identifier: Optional[str] = None,
    ):
        """Save the extracted piping line data as JSON in the exact format of extracted_piping_lines.json."""
        results = {
            "metadata": {
                "source_file": pdf_file,
                "extraction_timestamp": datetime.now().isoformat(),
                "total_found": len(piping_lines_data),
                "extraction_script": "process_pdf_to_piping_lines.py",
                "pid_identifier": pid_identifier,
            },
            "piping_lines": [],
        }

        # Convert the data to JSON-friendly format
        for piping_line in sorted(piping_lines_data.keys()):
            line_num, context, coords = piping_lines_data[piping_line]

            entry = {
                "piping_line_number": piping_line,
                "text_line_number": line_num,
                "context": context,
                "coordinates": coords if coords else None,
            }

            results["piping_lines"].append(entry)

        # Save to JSON file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    def process_pdf_to_piping_lines(
        self, pdf_path: str, output_json_path: str = None
    ) -> str:
        """Main method to process PDF and extract piping lines."""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not self.validate_environment_variables():
            raise ValueError("Missing required environment variables")

        # Generate output filename if not provided
        if output_json_path is None:
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_json_path = f"{base_name}_piping_lines.json"

        print(f"Processing: {pdf_path}")
        print(f"Output will be saved to: {output_json_path}")
        print("-" * 60)

        # Step 1: Process PDF with Document AI
        document_dict = self.process_pdf_with_document_ai(pdf_path)

        # Step 2: Extract text and layout information
        text, layout_info = self.extract_text_and_layout_from_document(document_dict)
        print(f"Extracted text length: {len(text)} characters")
        print(f"Layout info elements: {len(layout_info)}")

        # Step 3: Extract PID identifier
        pid_identifier = self.extract_pid_identifier(text)
        if pid_identifier:
            print(f"Found PID identifier: {pid_identifier}")
        else:
            print("PID identifier not found")

        # Step 4: Extract piping line numbers
        piping_lines_data = self.extract_piping_line_numbers(text, layout_info)

        # Step 5: Filter with additional validation
        validated_lines_data = {
            line: data
            for line, data in piping_lines_data.items()
            if self.validate_piping_line(line)
        }

        print(f"Found {len(validated_lines_data)} valid piping line numbers")

        # Step 6: Save results to JSON
        self.save_results_as_json(
            validated_lines_data, pdf_path, output_json_path, pid_identifier
        )

        print(f"Results saved to: {output_json_path}")

        # Print summary
        if validated_lines_data:
            print("\nExtracted piping line numbers:")
            for piping_line in sorted(validated_lines_data.keys()):
                line_num, context, coords = validated_lines_data[piping_line]
                print(f"  {piping_line} (line {line_num})")

        return output_json_path


def main():
    """Main function to handle command line usage."""
    if len(sys.argv) < 2:
        print(
            "Usage: python process_pdf_to_piping_lines.py <pdf_file> [output_json_file]"
        )
        print("Example: python process_pdf_to_piping_lines.py input.pdf")
        print("Example: python process_pdf_to_piping_lines.py input.pdf output.json")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_json_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        extractor = PipingLineExtractor()
        result_file = extractor.process_pdf_to_piping_lines(pdf_path, output_json_path)
        print(f"\n✅ Successfully processed PDF and saved results to: {result_file}")

    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
