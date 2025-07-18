#!/usr/bin/env python3
"""
Test Script for Mistral OCR - Multiple Bank Reports
This script tests Mistral OCR on multiple PDF files to compare performance against LlamaParse.
"""

import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Install required packages if not already installed
try:
    from mistralai import Mistral
except ImportError:
    print("Installing mistralai package...")
    os.system("pip install mistralai")
    from mistralai import Mistral

def setup_mistral_client():
    """Initialize Mistral client with API key from environment variables."""
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable is not set. Please add it to your .env file.")
    
    client = Mistral(api_key=api_key)
    print("✅ Mistral client initialized successfully")
    return client

def upload_file_to_mistral(client, file_path):
    """Upload local PDF file to Mistral and get signed URL."""
    try:
        print(f"📤 Uploading {file_path}...")
        
        with open(file_path, "rb") as file:
            uploaded_file = client.files.upload(
                file={"file_name": os.path.basename(file_path), "content": file},
                purpose="ocr"
            )
        
        print(f"✅ File uploaded. File ID: {uploaded_file.id}")
        
        # Get signed URL for OCR processing
        signed_url = client.files.get_signed_url(file_id=uploaded_file.id)
        print(f"✅ Signed URL obtained: {signed_url.url[:50]}...")
        
        return signed_url.url
    
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return None

def process_with_mistral_ocr(client, document_url, include_images=True):
    """Process document using Mistral OCR."""
    try:
        print("🔄 Starting Mistral OCR processing...")
        start_time = time.time()
        
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": document_url
            },
            include_image_base64=include_images
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"✅ OCR processing completed in {processing_time:.2f} seconds")
        print(f"📊 Pages processed: {len(ocr_response.pages)}")
        
        return ocr_response, processing_time
    
    except Exception as e:
        print(f"❌ Error during OCR processing: {e}")
        return None, None

def save_results(ocr_response, processing_time, file_name, output_dir="mistral_ocr_output"):
    """Save OCR results to files."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract base name without extension for output files
        base_name = os.path.splitext(file_name)[0]
        
        # Save markdown content
        markdown_content = []
        total_text_length = 0
        
        for i, page in enumerate(ocr_response.pages):
            page_md = f"<!-- Page {i + 1} -->\n\n{page.markdown}\n\n"
            markdown_content.append(page_md)
            total_text_length += len(page.markdown)
        
        # Write combined markdown (all pages in one file)
        markdown_file = os.path.join(output_dir, f"{base_name}_mistral.md")
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(markdown_content))  # Use double newlines instead of ---
        
        # Save processing stats
        # Handle usage_info serialization
        usage_info_dict = None
        if hasattr(ocr_response, 'usage_info') and ocr_response.usage_info:
            try:
                usage_info_dict = {
                    "pages_processed": getattr(ocr_response.usage_info, 'pages_processed', None),
                    "doc_size_bytes": getattr(ocr_response.usage_info, 'doc_size_bytes', None),
                }
            except Exception as e:
                print(f"⚠️  Warning: Could not serialize usage_info: {e}")
                usage_info_dict = None
        
        stats = {
            "file_name": file_name,
            "processing_time_seconds": processing_time,
            "total_pages": len(ocr_response.pages),
            "total_characters": total_text_length,
            "model": ocr_response.model if hasattr(ocr_response, 'model') else "mistral-ocr-latest",
            "processing_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "usage_info": usage_info_dict
        }
        
        stats_file = os.path.join(output_dir, f"{base_name}_stats.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        
        print(f"✅ Results saved to {output_dir}/")
        print(f"📄 Markdown file: {markdown_file}")
        print(f"📊 Processing stats: {stats_file}")
        
        return stats
    
    except Exception as e:
        print(f"❌ Error saving results: {e}")
        return None

def analyze_quality(stats):
    """Analyze the quality of OCR results."""
    print("\n" + "="*50)
    print("📈 QUALITY ANALYSIS")
    print("="*50)
    
    print(f"📄 Pages processed: {stats['total_pages']}")
    print(f"⏱️  Processing time: {stats['processing_time_seconds']:.2f} seconds")
    print(f"🚀 Pages per second: {stats['total_pages'] / stats['processing_time_seconds']:.2f}")
    print(f"📝 Total characters extracted: {stats['total_characters']:,}")
    print(f"📊 Average characters per page: {stats['total_characters'] // stats['total_pages']:,}")
    
    if stats.get('usage_info'):
        usage = stats['usage_info']
        if hasattr(usage, 'pages_processed'):
            print(f"✅ Pages processed (confirmed): {usage.pages_processed}")
        if hasattr(usage, 'doc_size_bytes'):
            print(f"📦 Document size: {usage.doc_size_bytes / (1024*1024):.2f} MB")

def process_single_file(client, file_path):
    """Process a single PDF file with Mistral OCR."""
    file_name = os.path.basename(file_path)
    print(f"\n🔍 Processing: {file_name}")
    print("="*60)
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"📁 Input file: {file_path}")
    print(f"📦 File size: {os.path.getsize(file_path) / (1024*1024):.2f} MB")
    
    # Upload file
    document_url = upload_file_to_mistral(client, file_path)
    if not document_url:
        return False
    
    # Process with OCR
    ocr_response, processing_time = process_with_mistral_ocr(client, document_url)
    if not ocr_response:
        return False
    
    # Save results
    stats = save_results(ocr_response, processing_time, file_name)
    if not stats:
        return False
    
    # Analyze quality
    analyze_quality(stats)
    
    print(f"✅ {file_name} processed successfully!")
    return True

def main():
    """Main function to run the Mistral OCR test on multiple files."""
    print("🧪 MISTRAL OCR TEST - Multiple Bank Reports")
    print("="*60)
    
    # Files to process
    files_to_process = [
        "psx_bank_reports/UBL_Quarterly_2022-06-30.pdf",
    ]
    
    print(f"📋 Files to process: {len(files_to_process)}")
    for file_path in files_to_process:
        print(f"   • {os.path.basename(file_path)}")
    
    # Setup Mistral client
    client = setup_mistral_client()
    
    # Process each file
    successful_files = []
    failed_files = []
    
    total_start_time = time.time()
    
    for file_path in files_to_process:
        try:
            success = process_single_file(client, file_path)
            if success:
                successful_files.append(os.path.basename(file_path))
            else:
                failed_files.append(os.path.basename(file_path))
        except Exception as e:
            print(f"❌ Unexpected error processing {file_path}: {e}")
            failed_files.append(os.path.basename(file_path))
    
    total_end_time = time.time()
    total_processing_time = total_end_time - total_start_time
    
    # Summary
    print("\n" + "="*60)
    print("📊 PROCESSING SUMMARY")
    print("="*60)
    print(f"⏱️  Total processing time: {total_processing_time:.2f} seconds")
    print(f"✅ Successfully processed: {len(successful_files)}")
    for file_name in successful_files:
        print(f"   • {file_name}")
    
    if failed_files:
        print(f"❌ Failed to process: {len(failed_files)}")
        for file_name in failed_files:
            print(f"   • {file_name}")
    
    print("\n💡 Next steps:")
    print("   1. Review the generated markdown files in mistral_ocr_output/")
    print("   2. Compare with the original LlamaParse outputs")
    print("   3. Check for financial statement extraction quality")

if __name__ == "__main__":
    main() 