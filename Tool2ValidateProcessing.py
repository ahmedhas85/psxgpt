import os
import json
import re
from collections import defaultdict
import sys

# Configuration
INPUT_DIR = "psx_markdown_clean"
OUTPUT_DIR = "output_metadata" 
VALIDATION_REPORT = "processing_validation_report.txt"

def get_chunk_numbers_from_markdown(markdown_file_path):
    """Extract all chunk numbers from a markdown file"""
    try:
        with open(markdown_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all "## Chunk X" headers
        pattern = r"##\s*Chunk\s*(\d+)\s*\n"
        matches = re.findall(pattern, content)
        return sorted([int(match) for match in matches])
    except Exception as e:
        return None, str(e)

def validate_json_file(json_file_path):
    """Validate a JSON metadata file"""
    results = {
        'valid_json': False,
        'chunk_count': 0,
        'chunk_numbers': [],
        'missing_fields': [],
        'invalid_entries': [],
        'financial_statements': {
            'profit_and_loss': 0,
            'balance_sheet': 0, 
            'cash_flow': 0,
            'changes_in_equity': 0,
            'comprehensive_income': 0
        },
        'statement_scopes': {
            'consolidated': 0,
            'unconsolidated': 0,
            'none': 0
        },
        'total_statements': 0,
        'total_notes': 0,
        'error': None
    }
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results['valid_json'] = True
        
        if not isinstance(data, list):
            results['error'] = f"JSON root is not a list, got {type(data)}"
            return results
        
        results['chunk_count'] = len(data)
        
        # Required fields for each chunk
        required_fields = [
            'chunk_number', 'financial_data', 'financial_statement_scope', 
            'is_statement', 'statement_type', 'is_note', 'note_link',
            'auditor_report', 'director_report', 'annual_report_discussion', 'file_name'
        ]
        
        for i, entry in enumerate(data):
            if not isinstance(entry, dict):
                results['invalid_entries'].append(f"Entry {i} is not a dict: {type(entry)}")
                continue
            
            # Check required fields
            missing = [field for field in required_fields if field not in entry]
            if missing:
                results['missing_fields'].extend([f"Entry {i} missing: {', '.join(missing)}"])
            
            # Collect chunk numbers
            if 'chunk_number' in entry:
                results['chunk_numbers'].append(entry['chunk_number'])
            
            # Validate financial_data field
            if entry.get('financial_data') != 'yes':
                results['invalid_entries'].append(f"Entry {i} has financial_data != 'yes': {entry.get('financial_data')}")
            
            # Count financial statements
            if entry.get('is_statement') == 'yes':
                results['total_statements'] += 1
                statement_type = entry.get('statement_type', 'none')
                if statement_type in results['financial_statements']:
                    results['financial_statements'][statement_type] += 1
                
                # Count statement scopes
                scope = entry.get('financial_statement_scope', 'none')
                if scope in results['statement_scopes']:
                    results['statement_scopes'][scope] += 1
            
            # Count notes
            if entry.get('is_note') == 'yes':
                results['total_notes'] += 1
        
        results['chunk_numbers'] = sorted(results['chunk_numbers'])
        
    except json.JSONDecodeError as e:
        results['error'] = f"JSON decode error: {str(e)}"
    except Exception as e:
        results['error'] = f"Unexpected error: {str(e)}"
    
    return results

def validate_processing():
    """Main validation function"""
    
    print("🔍 Starting Processing Validation...")
    print(f"Input directory: {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("-" * 50)
    
    # Get all markdown files
    if not os.path.exists(INPUT_DIR):
        print(f"❌ Input directory '{INPUT_DIR}' not found!")
        return
    
    if not os.path.exists(OUTPUT_DIR):
        print(f"❌ Output directory '{OUTPUT_DIR}' not found!")
        return
    
    markdown_files = sorted([f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.md')])
    
    if not markdown_files:
        print(f"❌ No markdown files found in '{INPUT_DIR}'!")
        return
    
    print(f"📁 Found {len(markdown_files)} markdown files to validate")
    
    # Validation results
    results = {
        'total_files': len(markdown_files),
        'processed_files': 0,
        'missing_output': [],
        'empty_output': [],
        'json_errors': [],
        'chunk_coverage_issues': [],
        'validation_warnings': [],
        'statement_detection_issues': [],
        'successful_files': [],
        'total_chunks_expected': 0,
        'total_chunks_processed': 0,
        'total_statements_found': 0,
        'total_notes_found': 0,
        'files_with_all_statements': [],
        'files_missing_core_statements': []
    }
    
    # Validate each file
    for md_file in markdown_files:
        md_path = os.path.join(INPUT_DIR, md_file)
        json_file = os.path.splitext(md_file)[0] + '.json'
        json_path = os.path.join(OUTPUT_DIR, json_file)
        
        print(f"\n📋 Validating: {md_file}")
        
        # Check if output file exists
        if not os.path.exists(json_path):
            print(f"  ❌ Missing output file: {json_file}")
            results['missing_output'].append(md_file)
            continue
        
        # Get expected chunks from markdown
        expected_chunks = get_chunk_numbers_from_markdown(md_path)
        if expected_chunks is None:
            print(f"  ⚠️ Could not read markdown file")
            results['validation_warnings'].append(f"{md_file}: Could not read markdown")
            continue
        
        if isinstance(expected_chunks, tuple):  # Error case
            print(f"  ⚠️ Error reading markdown: {expected_chunks[1]}")
            results['validation_warnings'].append(f"{md_file}: {expected_chunks[1]}")
            continue
        
        results['total_chunks_expected'] += len(expected_chunks)
        print(f"  📊 Expected chunks: {len(expected_chunks)} (range: {min(expected_chunks) if expected_chunks else 'N/A'}-{max(expected_chunks) if expected_chunks else 'N/A'})")
        
        # Validate JSON output
        json_validation = validate_json_file(json_path)
        
        if json_validation['error']:
            print(f"  ❌ JSON error: {json_validation['error']}")
            results['json_errors'].append(f"{md_file}: {json_validation['error']}")
            continue
        
        if not json_validation['valid_json']:
            print(f"  ❌ Invalid JSON structure")
            results['json_errors'].append(f"{md_file}: Invalid JSON structure")
            continue
        
        processed_chunks = json_validation['chunk_numbers']
        results['total_chunks_processed'] += len(processed_chunks)
        
        print(f"  ✅ Processed chunks: {len(processed_chunks)}")
        
        # Check for empty output
        if len(processed_chunks) == 0:
            print(f"  ⚠️ No financial chunks found (empty output)")
            results['empty_output'].append(md_file)
        
        # Check chunk coverage
        if expected_chunks and processed_chunks:
            missing_chunks = []
            
            # Find gaps in processed chunks
            if processed_chunks:
                min_processed = min(processed_chunks)
                max_processed = max(processed_chunks)
                
                # Check if we're missing chunks in the expected range
                # Only flag as missing if we have some processed chunks but are missing others in sequence
                for chunk_num in expected_chunks:
                    if chunk_num >= min_processed and chunk_num <= max_processed and chunk_num not in processed_chunks:
                        missing_chunks.append(chunk_num)
            
            if missing_chunks:
                print(f"  ⚠️ Missing chunks in sequence: {missing_chunks[:10]}{'...' if len(missing_chunks) > 10 else ''}")
                results['chunk_coverage_issues'].append(f"{md_file}: Missing {len(missing_chunks)} chunks in sequence")
        
        # Check for field validation issues
        if json_validation['missing_fields']:
            print(f"  ⚠️ Field issues: {len(json_validation['missing_fields'])} entries with missing fields")
            results['validation_warnings'].extend([f"{md_file}: {issue}" for issue in json_validation['missing_fields'][:3]])
        
        if json_validation['invalid_entries']:
            print(f"  ⚠️ Data issues: {len(json_validation['invalid_entries'])} invalid entries")
            results['validation_warnings'].extend([f"{md_file}: {issue}" for issue in json_validation['invalid_entries'][:3]])
        
        # Financial Statement Detection Validation
        statement_data = json_validation['financial_statements']
        results['total_statements_found'] += json_validation['total_statements']
        results['total_notes_found'] += json_validation['total_notes']
        
        # Check for core financial statements
        core_statements = ['profit_and_loss', 'balance_sheet', 'cash_flow', 'changes_in_equity']
        found_statements = [stmt for stmt in core_statements if statement_data[stmt] > 0]
        missing_statements = [stmt for stmt in core_statements if statement_data[stmt] == 0]
        
        print(f"  📊 Financial statements found: {json_validation['total_statements']} statements, {json_validation['total_notes']} notes")
        
        if found_statements:
            print(f"    ✅ Detected: {', '.join(found_statements)}")
        
        if missing_statements:
            print(f"    ⚠️ Missing: {', '.join(missing_statements)}")
            results['statement_detection_issues'].append(f"{md_file}: Missing {', '.join(missing_statements)}")
            results['files_missing_core_statements'].append(md_file)
        else:
            results['files_with_all_statements'].append(md_file)
        
        # Check scope distribution
        scopes = json_validation['statement_scopes']
        if scopes['consolidated'] > 0 and scopes['unconsolidated'] > 0:
            print(f"    📋 Scopes: {scopes['consolidated']} consolidated, {scopes['unconsolidated']} unconsolidated")
        elif scopes['consolidated'] > 0:
            print(f"    📋 Scope: {scopes['consolidated']} consolidated statements")
        elif scopes['unconsolidated'] > 0:
            print(f"    📋 Scope: {scopes['unconsolidated']} unconsolidated statements")
        else:
            print(f"    ⚠️ No scope identified for statements")
        
        # Validate statement detection quality
        if json_validation['total_statements'] == 0 and len(processed_chunks) > 10:
            print(f"  ⚠️ No financial statements detected despite {len(processed_chunks)} financial chunks")
            results['statement_detection_issues'].append(f"{md_file}: No statements found in {len(processed_chunks)} chunks")
        
        # Mark as successfully processed if no major issues
        if (json_validation['valid_json'] and 
            not json_validation['error'] and 
            len(processed_chunks) > 0):
            results['successful_files'].append(md_file)
            print(f"  ✅ Validation passed")
        
        results['processed_files'] += 1
    
    # Generate summary report
    print("\n" + "="*60)
    print("📋 VALIDATION SUMMARY")
    print("="*60)
    
    print(f"Total markdown files: {results['total_files']}")
    print(f"Successfully processed: {len(results['successful_files'])}")
    print(f"Missing output files: {len(results['missing_output'])}")
    print(f"Empty output files: {len(results['empty_output'])}")
    print(f"Files with JSON errors: {len(results['json_errors'])}")
    print(f"Files with chunk coverage issues: {len(results['chunk_coverage_issues'])}")
    print(f"Files with statement detection issues: {len(results['statement_detection_issues'])}")
    print(f"Files with validation warnings: {len(results['validation_warnings'])}")
    
    print(f"\nChunk Statistics:")
    print(f"Total chunks expected: {results['total_chunks_expected']}")
    print(f"Total chunks processed: {results['total_chunks_processed']}")
    if results['total_chunks_expected'] > 0:
        coverage_pct = (results['total_chunks_processed'] / results['total_chunks_expected']) * 100
        print(f"Overall coverage: {coverage_pct:.1f}%")
    
    print(f"\nFinancial Statement Detection:")
    print(f"Total statements found: {results['total_statements_found']}")
    print(f"Total notes found: {results['total_notes_found']}")
    print(f"Files with all core statements: {len(results['files_with_all_statements'])}")
    print(f"Files missing core statements: {len(results['files_missing_core_statements'])}")
    
    # Write detailed report
    with open(VALIDATION_REPORT, 'w', encoding='utf-8') as f:
        f.write("PROCESSING VALIDATION REPORT\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Generated: {__import__('datetime').datetime.now()}\n\n")
        
        f.write("SUMMARY:\n")
        f.write(f"  Total files: {results['total_files']}\n")
        f.write(f"  Successful: {len(results['successful_files'])}\n")
        f.write(f"  Missing output: {len(results['missing_output'])}\n")
        f.write(f"  Empty output: {len(results['empty_output'])}\n")
        f.write(f"  JSON errors: {len(results['json_errors'])}\n")
        f.write(f"  Coverage issues: {len(results['chunk_coverage_issues'])}\n")
        f.write(f"  Statement detection issues: {len(results['statement_detection_issues'])}\n")
        f.write(f"  Validation warnings: {len(results['validation_warnings'])}\n\n")
        
        f.write("FINANCIAL STATEMENT DETECTION:\n")
        f.write(f"  Total statements found: {results['total_statements_found']}\n")
        f.write(f"  Total notes found: {results['total_notes_found']}\n")
        f.write(f"  Files with all core statements: {len(results['files_with_all_statements'])}\n")
        f.write(f"  Files missing core statements: {len(results['files_missing_core_statements'])}\n\n")
        
        if results['missing_output']:
            f.write("MISSING OUTPUT FILES:\n")
            for file in results['missing_output']:
                f.write(f"  - {file}\n")
            f.write("\n")
        
        if results['empty_output']:
            f.write("EMPTY OUTPUT FILES:\n")
            for file in results['empty_output']:
                f.write(f"  - {file}\n")
            f.write("\n")
        
        if results['json_errors']:
            f.write("JSON ERRORS:\n")
            for error in results['json_errors']:
                f.write(f"  - {error}\n")
            f.write("\n")
        
        if results['chunk_coverage_issues']:
            f.write("CHUNK COVERAGE ISSUES:\n")
            for issue in results['chunk_coverage_issues']:
                f.write(f"  - {issue}\n")
            f.write("\n")
        
        if results['statement_detection_issues']:
            f.write("FINANCIAL STATEMENT DETECTION ISSUES:\n")
            for issue in results['statement_detection_issues']:
                f.write(f"  - {issue}\n")
            f.write("\n")
        
        if results['validation_warnings']:
            f.write("VALIDATION WARNINGS:\n")
            for warning in results['validation_warnings'][:20]:  # Limit to first 20
                f.write(f"  - {warning}\n")
            if len(results['validation_warnings']) > 20:
                f.write(f"  ... and {len(results['validation_warnings']) - 20} more warnings\n")
            f.write("\n")
        
        f.write("SUCCESSFULLY PROCESSED FILES:\n")
        for file in results['successful_files']:
            f.write(f"  ✅ {file}\n")
    
    print(f"\n📄 Detailed report saved to: {VALIDATION_REPORT}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if results['missing_output']:
        print(f"  - Reprocess {len(results['missing_output'])} files with missing output")
    if results['json_errors']:
        print(f"  - Fix JSON errors in {len(results['json_errors'])} files")
    if results['chunk_coverage_issues']:
        print(f"  - Review {len(results['chunk_coverage_issues'])} files with chunk coverage issues")
    if results['statement_detection_issues']:
        print(f"  - Check {len(results['statement_detection_issues'])} files with statement detection issues")
        print(f"    These files may need manual review or prompt adjustment")
    if results['files_missing_core_statements']:
        print(f"  - {len(results['files_missing_core_statements'])} files are missing core financial statements")
        print(f"    This could indicate AI detection issues or unusual report structures")
    if len(results['successful_files']) == results['total_files'] and not results['statement_detection_issues']:
        print(f"  🎉 All files processed successfully with good statement detection!")
    
    # Return results for programmatic use
    return results

if __name__ == "__main__":
    validate_processing() 