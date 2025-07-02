# OCR Quality Evaluation Framework

A practical Python framework for quickly evaluating OCR (Optical Character Recognition) output quality. This tool provides rapid assessment of text extraction accuracy to help you compare different OCR tools, settings, and methodologies.

## 🎯 Why This Approach?

**The Problem**: You've run documents through OCR software, but how do you know if the text extraction worked well? Manual checking is time-consuming and subjective.

**Our Solution**: This framework automatically evaluates OCR output by analysing the linguistic quality of extracted text. Poor OCR produces text with spelling mistakes, grammar errors, and nonsensical character combinations - exactly what this tool detects.

**Use Case**: Perfect for comparing OCR results from different tools (Tesseract vs EasyOCR vs PaddleOCR) or testing different OCR settings on the same document set.

## 🔍 How It Works

### The Process
1. **Extract Text**: Pulls text from your OCR-processed PDFs
2. **Language Analysis**: Runs sophisticated grammar and spelling checks using LanguageTool
3. **Error Counting**: Tallies mistakes per 100 words (industry-standard metric)
4. **Quality Scoring**: Combines multiple indicators into an overall quality score
5. **Comparison Ready**: Outputs standardised metrics for easy OCR tool comparison

### What Gets Measured
- **Spelling Errors**: Misspelled words (indicates character recognition failures)
- **Grammar Errors**: Sentence structure issues (shows word boundary problems)
- **Valid Words**: Percentage of recognisable English words
- **Error Density**: Mistakes per 100 words (primary quality metric)
- **Overall Score**: Weighted assessment combining all factors

## 📊 What The Output Tells You

The framework generates a CSV report with quality metrics for each document:

**Key Metrics:**
- **Errors per 100 Words**: Lower values indicate better text quality (aim for <5)
- **Valid Word %**: Higher percentages show better recognition accuracy (aim for >80%)  
- **Quality Score**: 0-100 scale (90+ excellent, 60-89 good, <40 poor)
- **Quality Rating**: Simple classification (Excellent/Good/Fair/Poor/Very Poor)

**Example Output:**
```
Document A: 2.3 errors/100 words, 92% valid words → "Excellent" OCR
Document B: 15.7 errors/100 words, 67% valid words → "Poor" OCR
```

## ⚠️ Limitations & Constraints

**This tool provides a glimpse of word-level accuracy only.** Understanding these limitations is crucial for proper interpretation of results.

### What This Framework Cannot Do
1. **Detect Missing Text**: Won't identify content OCR completely missed
2. **Evaluate Text Coherence**: Doesn't check if sentences make logical sense
3. **Structure Analysis**: Ignores layout, tables, or formatting preservation
4. **Semantic Accuracy**: Whether technical terms are correctly interpreted
5. **Completeness Assessment**: How much of the original document was captured
6. **Absolute Quality Measurement**: Provides relative comparison, not absolute accuracy

### Technical Constraints
- **Language Dependent**: Optimised for English text (other languages supported but less accurate)
- **Context Blind**: Doesn't understand document type or domain-specific terminology
- **Surface Level Analysis**: Focuses on character/word accuracy, not meaning preservation
- **PDF Extraction Dependent**: Quality limited by PyPDF2's text extraction capabilities
- **Grammar Model Limits**: LanguageTool may miss domain-specific errors or flag technical terms
- **Memory Intensive**: Large documents may require significant RAM
- **Processing Speed**: LanguageTool analysis can be slow for large document sets

### Scope Boundaries
- **Quality Assessment Only**: Tells you *how well* OCR worked, not *what went wrong*
- **Comparative Tool**: Best used for comparing OCR approaches, not absolute quality judgment
- **Rapid Screening**: Designed for quick evaluation, not comprehensive analysis
- **English-Centric**: Optimised for English, less accurate for other languages

## 🚀 Installation & Setup

### Prerequisites

#### 1. Java 24 (Required)
LanguageTool requires **Java 17 or higher**. This framework was developed and tested specifically with **Java 24**.

**Check current version:**
```bash
java -version
```

**Install Java 24 (recommended):**
1. Download Java 24 from https://www.oracle.com/java/technologies/downloads/?er=221886
2. Install and add to system PATH
3. Restart terminal and verify: `java -version` shows 24+

**⚠️ Important**: The script does not verify your Java version automatically. You must ensure Java 17+ is properly installed and accessible, or LanguageTool will fail during initialization.

#### 2. Python Dependencies
```bash
pip install PyPDF2 language-tool-python
```

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Test with single file
python simple_ocr_evaluator.py document.pdf results.csv

# Analyse entire directory
python simple_ocr_evaluator.py ./ocr_output/ results.csv
```

## 📖 Usage Examples

### Basic Commands

```bash
# Single PDF analysis
python simple_ocr_evaluator.py document.pdf results.csv

# Directory analysis  
python simple_ocr_evaluator.py ./pdf_folder/ results.csv

# Quiet mode (no progress output)
python simple_ocr_evaluator.py ./pdfs/ results.csv --quiet

# British English grammar
python simple_ocr_evaluator.py ./pdfs/ results.csv --language en-GB
```

### OCR Comparison Workflow

**Step 1: Baseline** (original scans - should show poor quality)
```bash
python simple_ocr_evaluator.py ./original_scans/ baseline.csv
```

**Step 2: Test OCR Tool A**
```bash
python simple_ocr_evaluator.py ./tesseract_output/ tesseract.csv
```

**Step 3: Test OCR Tool B**
```bash
python simple_ocr_evaluator.py ./adobe_output/ adobe.csv
```

**Step 4: Compare Results**
Open CSV files and compare "Errors per 100 Words" - lower values indicate better OCR performance.

## 🔧 Command Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `input` | PDF file or directory | Required | `./pdfs/` |
| `output` | CSV output file | Required | `results.csv` |
| `--language` | Grammar checking language | `en-US` | `--language en-GB` |
| `--quiet` | Suppress progress output | Off | `--quiet` |
| `--help` | Show help information | - | `--help` |

### Supported Languages
- `en-GB` - British English
- `en-US` - American English  
- `es` - Spanish
- `fr` - French
- `de` - German
- [Full list](https://languagetool.org/languages/)

## 🔒 Privacy & Local Processing

**Complete local processing** - your documents never leave your machine:
- ✅ All analysis performed locally using Java/Python
- ✅ No cloud services or external APIs
- ✅ Works offline after initial setup
- ✅ One-time download of language models (~50MB)

## 📊 Understanding Results

### Quality Classifications
- **Excellent** (90+ score): Production ready, minimal errors
- **Good** (75-89 score): Minor cleanup needed  
- **Fair** (60-74 score): Moderate editing required
- **Poor** (40-59 score): Significant quality issues
- **Very Poor** (<40 score): OCR largely failed

### Key Comparison Metrics
1. **Errors per 100 Words**: Primary indicator (lower = better)
2. **Valid Word Percentage**: Recognition accuracy (higher = better)
3. **Quality Score**: Overall assessment (higher = better)

### Interpreting Results
- **<2 errors/100 words**: Excellent OCR, ready for automated processing
- **2-5 errors/100 words**: Good OCR, minimal manual correction needed
- **5-10 errors/100 words**: Fair OCR, moderate editing required
- **>20 errors/100 words**: Poor OCR, consider re-processing with different settings

## 🔮 Future Enhancements

### Planned Improvements

#### 1. Perplexity Evaluation
**What it is**: Uses AI language models to measure how "surprising" or incoherent text appears to a computer.

**How it helps**: 
- Detects text that looks like words but makes no sense
- Identifies OCR output that passes spell-check but is gibberish
- Provides semantic coherence measurement

**Implementation**: Add GPT-2 based perplexity scoring for text coherence assessment.

#### 2. Ground Truth Dataset Creation
**What it is**: Manually verified "perfect" text versions of test documents for absolute accuracy measurement.

**How it helps**:
- Enables character-level accuracy calculation
- Provides objective benchmarking
- Allows measurement of OCR recall (how much text was captured)

**Implementation**: Tools for creating and comparing against reference texts.

#### 3. Enhanced Error Classification
- Distinguish between character substitution vs insertion/deletion errors
- Identify common OCR failure patterns
- Provide specific recommendations for OCR parameter tuning

#### 4. Layout Analysis Integration
- Detect table extraction quality
- Evaluate formatting preservation
- Assess reading order accuracy

## 🛠️ Troubleshooting

### Common Issues

**"Java version < 17" error**
- Install Java 24 from Oracle's website
- Update system PATH to point to new Java installation

**"LanguageTool initialization failed"**
- Check internet connection (needed for first-time model download)
- Verify firewall isn't blocking LanguageTool

**Slow processing**
- Use `--quiet` mode to reduce output overhead
- Process smaller document batches
- Ensure sufficient RAM available

**Memory errors**
- Process files individually rather than large directories
- Close other applications to free memory
- Consider processing overnight for large collections

## 📄 Project Structure

```
OCR-eval/
├── simple_ocr_evaluator.py    # Main evaluation script
├── requirements.txt           # Python dependencies  
├── README.md                 # This documentation
└── results.csv              # Generated outpugiyt file
```

**Ready to evaluate your OCR quality?** Start with a test run:
```bash
python simple_ocr_evaluator.py sample_document.pdf test_results.csv
```