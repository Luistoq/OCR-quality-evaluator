#!/usr/bin/env python3
"""
Simple OCR Quality Evaluator using LanguageTool
Evaluates OCR quality by counting grammar/spelling errors and valid words
"""

import os
import csv
import sys
import argparse
import statistics
from pathlib import Path
from collections import Counter
from PyPDF2 import PdfReader
import logging

# Enhanced requirements for this approach
try:
    import language_tool_python
except ImportError:
    print("Error: language_tool_python not installed.")
    print("Install with: pip install language-tool-python")
    sys.exit(1)

# Silence warnings
logging.basicConfig(level=logging.ERROR)

class LanguageQualityEvaluator:
    """LanguageTool-based grammar and spelling evaluation"""
    
    def __init__(self, language='en-US'):
        try:
            print("Initializing LanguageTool (this may take a moment)...")
            self.tool = language_tool_python.LanguageTool(language)
            print("LanguageTool ready!")
        except Exception as e:
            print(f"Error initializing LanguageTool: {e}")
            print("This might be due to Java not being installed or network issues.")
            raise
    
    def evaluate_text(self, text):
        """Evaluate text quality using LanguageTool"""
        if not text.strip():
            return {
                'total_errors': 0,
                'errors_per_100_words': 0,
                'spelling_errors': 0,
                'grammar_errors': 0,
                'word_count': 0,
                'error_types': {},
                'valid_words': 0,
                'valid_word_percentage': 0
            }
        
        try:
            # Get errors from LanguageTool
            matches = self.tool.check(text)
            
            # Count words
            words = text.split()
            word_count = len(words)
            
            # Count valid words (words not flagged by LanguageTool)
            flagged_positions = set()
            for match in matches:
                # Get the position range of the error
                start_pos = match.offset
                end_pos = match.offset + match.errorLength
                flagged_positions.add((start_pos, end_pos))
            
            # Calculate valid words (approximate - words not in error regions)
            valid_words = self.estimate_valid_words(text, flagged_positions, word_count)
            valid_word_percentage = (valid_words / word_count * 100) if word_count > 0 else 0
            
            # Categorize errors
            spelling_errors = 0
            grammar_errors = 0
            error_types = Counter()
            
            for match in matches:
                category = match.category
                error_types[category] += 1
                
                # Classify error type (spelling vs grammar)
                if any(keyword in category.upper() for keyword in ['TYPO', 'MORFOLOGIK', 'SPELL']):
                    spelling_errors += 1
                else:
                    grammar_errors += 1
            
            # Calculate errors per 100 words
            errors_per_100 = (len(matches) / word_count * 100) if word_count > 0 else 0
            
            return {
                'total_errors': len(matches),
                'errors_per_100_words': errors_per_100,
                'spelling_errors': spelling_errors,
                'grammar_errors': grammar_errors,
                'word_count': word_count,
                'error_types': dict(error_types),
                'valid_words': valid_words,
                'valid_word_percentage': valid_word_percentage
            }
            
        except Exception as e:
            print(f"Warning: LanguageTool evaluation failed: {e}")
            word_count = len(text.split())
            return {
                'total_errors': 0,
                'errors_per_100_words': 0,
                'spelling_errors': 0,
                'grammar_errors': 0,
                'word_count': word_count,
                'error_types': {},
                'valid_words': word_count,  # Assume all valid if check failed
                'valid_word_percentage': 100
            }
    
    def estimate_valid_words(self, text, flagged_positions, total_words):
        """Estimate number of valid words based on error positions"""
        if not flagged_positions:
            return total_words
        
        # A single spelling error affects one word, while a grammar error might span two or more; 1.5 is a balanced average
        estimated_affected_words = len(flagged_positions) * 1.5
        valid_words = max(0, total_words - estimated_affected_words)
        
        return int(valid_words)
    
    def __del__(self):
        """Clean up LanguageTool"""
        if hasattr(self, 'tool'):
            try:
                self.tool.close()
            except:
                pass

def extract_pdf_text(file_path):
    """Extract text from PDF file"""
    try:
        reader = PdfReader(file_path)
        text = ""
        page_count = len(reader.pages)
        
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
        
        return text.strip(), page_count
    except Exception as e:
        print(f"Warning: Could not extract text from {file_path}: {e}")
        return "", 0

def evaluate_pdf_quality(file_path, lang_evaluator, root_dir=None):
    """Evaluate PDF quality using LanguageTool"""
    file_dir, filename = os.path.split(file_path)
    
    # Handle relative directory calculation
    if root_dir:
        relative_dir = os.path.relpath(file_dir, root_dir)
    else:
        relative_dir = file_dir
    
    try:
        # Extract text from PDF
        text, page_count = extract_pdf_text(file_path)
        
        if not text.strip():
            return [
                relative_dir, filename, page_count, 0, 0, "No text extracted",
                0, 0, 0, 0, 0, 0, 0, "None", 0, "No Text"
            ]
        
        # Basic text metrics
        word_count = len(text.split())
        char_count = len(text)
        words_per_page = word_count / page_count if page_count > 0 else 0
        
        # LanguageTool evaluation
        lang_results = lang_evaluator.evaluate_text(text)
        
        # Calculate quality score
        quality_score = calculate_quality_score(lang_results)
        quality_rating = classify_quality(quality_score, lang_results['errors_per_100_words'])
        
        # Get most common error type
        most_common_error = get_most_common_error_type(lang_results['error_types'])
        
        return [
            relative_dir,
            filename,
            page_count,
            word_count,
            f"{words_per_page:.1f}",
            f"{char_count}",
            lang_results['total_errors'],
            f"{lang_results['errors_per_100_words']:.2f}",
            lang_results['spelling_errors'],
            lang_results['grammar_errors'],
            len(lang_results['error_types']),
            lang_results['valid_words'],
            f"{lang_results['valid_word_percentage']:.1f}%",
            most_common_error,
            f"{quality_score:.1f}",
            quality_rating
        ]
        
    except Exception as e:
        return [
            relative_dir, filename, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, str(e)[:30], 0, "Error"
        ]

def calculate_quality_score(lang_results):
    """Calculate overall quality score (0-100) based on language metrics"""
    word_count = lang_results['word_count']
    if word_count == 0:
        return 0
    
    # Start with base score
    score = 100
    
    # Major penalty for high error rate
    error_rate = lang_results['errors_per_100_words']
    if error_rate > 0:
        # Exponential penalty for high error rates
        error_penalty = min(80, error_rate * 3)  # Cap at 80 points lost
        score -= error_penalty
    
    # Penalty for very short text (likely extraction failure)
    if word_count < 10:
        score -= 30
    elif word_count < 50:
        score -= 15
    
    # Bonus for having many valid words
    valid_word_pct = lang_results['valid_word_percentage']
    if valid_word_pct > 90:
        score += 5
    elif valid_word_pct < 70:
        score -= 10
    
    # Small penalty for too many error categories (indicates chaos)
    error_categories = len(lang_results['error_types'])
    if error_categories > 5:
        score -= error_categories
    
    return max(0, min(100, score))

def classify_quality(score, errors_per_100):
    """Classify quality based on score and error rate"""
    if score >= 90 and errors_per_100 < 2:
        return "Excellent"
    elif score >= 75 and errors_per_100 < 5:
        return "Good"  
    elif score >= 60 and errors_per_100 < 10:
        return "Fair"
    elif score >= 40 and errors_per_100 < 20:
        return "Poor"
    else:
        return "Very Poor"

def get_most_common_error_type(error_types):
    """Get most common error type"""
    if not error_types:
        return "None"
    return max(error_types, key=error_types.get)

def find_pdf_files(input_path):
    """Find PDF files from input path (file or directory)"""
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {input_path}")
    
    pdf_files = []
    
    if input_path.is_file():
        if input_path.suffix.lower() == '.pdf':
            pdf_files.append(str(input_path))
            return pdf_files, input_path.parent
        else:
            raise ValueError(f"Input file is not a PDF: {input_path}")
    
    elif input_path.is_dir():
        for pdf_file in input_path.rglob('*.pdf'):
            pdf_files.append(str(pdf_file))
        return pdf_files, input_path
    
    else:
        raise ValueError(f"Invalid input path: {input_path}")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Simple OCR Quality Evaluator using LanguageTool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze single PDF file
  python simple_ocr_evaluator.py document.pdf results.csv
  
  # Analyze all PDFs in directory
  python simple_ocr_evaluator.py ./pdf_folder/ results.csv
  
  # Use different language
  python simple_ocr_evaluator.py ./pdfs/ results.csv --language en-GB
  
  # Quiet mode
  python simple_ocr_evaluator.py ./pdfs/ results.csv --quiet

OCR Comparison Workflow:
  1. python simple_ocr_evaluator.py ./original_scans/ baseline.csv
  2. python simple_ocr_evaluator.py ./tesseract_output/ tesseract.csv  
  3. python simple_ocr_evaluator.py ./abbyy_output/ abbyy.csv
  4. Compare "Errors per 100 Words" and "Quality Score" columns
        """
    )
    
    parser.add_argument('input', help='Input PDF file or directory')
    parser.add_argument('output', help='Output CSV file path')
    
    parser.add_argument(
        '--language',
        default='en-US',
        help='LanguageTool language code (default: en-US)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Simple OCR Evaluator v1.0'
    )
    
    return parser.parse_args()

def print_statistics(results, quiet=False):
    """Print comprehensive statistics"""
    if quiet:
        return
    
    valid_results = [r for r in results if r[15] != "Error" and r[15] != "No Text"]
    
    if not valid_results:
        print("\nNo valid results for analysis.")
        return
    
    # Calculate statistics
    total_docs = len(results)
    valid_docs = len(valid_results)
    
    # Quality distribution
    quality_counts = Counter(r[15] for r in results)
    
    # Error statistics
    error_rates = [float(r[7]) for r in valid_results if r[7] != "0"]
    avg_error_rate = statistics.mean(error_rates) if error_rates else 0
    
    # Quality scores
    quality_scores = [float(r[14]) for r in valid_results]
    avg_quality = statistics.mean(quality_scores) if quality_scores else 0
    
    # Valid word percentages
    valid_word_pcts = [float(r[12].replace('%', '')) for r in valid_results if r[12] != "0%"]
    avg_valid_words = statistics.mean(valid_word_pcts) if valid_word_pcts else 0
    
    print(f"\n{'='*60}")
    print("OCR QUALITY EVALUATION REPORT (LanguageTool)")
    print(f"{'='*60}")
    print(f"Total Documents: {total_docs}")
    print(f"Documents with Text: {valid_docs} ({valid_docs/total_docs*100:.1f}%)")
    
    print(f"\nQuality Distribution:")
    for quality, count in quality_counts.most_common():
        print(f"  {quality}: {count} ({count/total_docs*100:.1f}%)")
    
    print(f"\nAverage Metrics:")
    print(f"  Quality Score: {avg_quality:.1f}/100")
    print(f"  Errors per 100 words: {avg_error_rate:.2f}")
    print(f"  Valid words: {avg_valid_words:.1f}%")
    
    # Best and worst documents
    if quality_scores:
        best_doc = max(valid_results, key=lambda x: float(x[14]))
        worst_doc = min(valid_results, key=lambda x: float(x[14]))
        
        print(f"\nBest Document: {best_doc[1]} (Score: {best_doc[14]})")
        print(f"Worst Document: {worst_doc[1]} (Score: {worst_doc[14]})")
        
    print(f"\n💡 Lower 'Errors per 100 Words' = Better OCR")
    print(f"💡 Higher 'Quality Score' = Better OCR")
    print(f"💡 Higher 'Valid Word %' = Better OCR")

def main():
    args = parse_arguments()
    
    try:
        # Find PDF files
        pdf_files, root_dir = find_pdf_files(args.input)
        
        if not pdf_files:
            print(f"No PDF files found in: {args.input}")
            sys.exit(1)
        
        if not args.quiet:
            input_type = "file" if len(pdf_files) == 1 else "directory"
            print(f"Found {len(pdf_files)} PDF file(s) to evaluate from {input_type}")
        
        # Initialize LanguageTool
        lang_evaluator = LanguageQualityEvaluator(args.language)
        
        # Process PDFs (single-threaded to avoid LanguageTool conflicts)
        results = []
        
        for i, pdf_file in enumerate(pdf_files):
            if not args.quiet:
                print(f"Processing {i+1}/{len(pdf_files)}: {Path(pdf_file).name}")
            
            result = evaluate_pdf_quality(pdf_file, lang_evaluator, root_dir)
            results.append(result)
        
        # Write results
        headers = [
            'Relative Directory', 'Filename', 'Pages', 'Word Count', 'Words/Page', 'Characters',
            'Total Errors', 'Errors per 100 Words', 'Spelling Errors', 'Grammar Errors',
            'Error Categories', 'Valid Words', 'Valid Word %', 'Most Common Error',
            'Quality Score', 'Quality Rating'
        ]
        
        with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
            # Sort by quality score (best first)
            results.sort(key=lambda x: float(x[14]) if x[14] != "0" else 0, reverse=True)
            writer.writerows(results)
        
        # Print statistics
        print_statistics(results, args.quiet)
        
        if not args.quiet:
            print(f"\nResults saved to: {args.output}")
            print("\n🎯 Use this to compare OCR tools:")
            print("   - Lower 'Errors per 100 Words' = Better OCR")
            print("   - Higher 'Quality Score' = Better OCR")
            print("   - Higher 'Valid Word %' = Better OCR")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Clean up LanguageTool
        if 'lang_evaluator' in locals():
            del lang_evaluator

if __name__ == "__main__":
    main()