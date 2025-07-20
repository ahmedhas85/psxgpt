# psxGPT

A ChatGPT-like application for Pakistan Stock Exchange (PSX) financial data, which can be repurposed for any financial data including querying a data room during acquisition due diligence.

## What psxGPT Does

psxGPT allows financial analysts to query and analyze financial data using plain English. For example:

*"Get me Deposits per branch for HBL, UBL and MEBL in 2024"*

psxGPT will find the necessary information and compile a report using ONLY data found in financial reports.

**Use Cases:**
- Financial statement analysis and comparison
- Due diligence data room queries
- Regulatory filing research
- Querying Economic Survey of Pakistan or SBP Annual Report

## How It Works

psxGPT processes financial documents through an 8-step pipeline:

1. **Download PDFs** (`Step1DownloadPDFsSearch.py` or `Step1DownloadPDFsTickers.py`)
2. **Convert to Markdown** (`Step2ConvertPDFtoMarkdown.py`) - Uses LlamaParse or `Tool1Mistral_OCR.py` for scanned documents
3. **Create Chunks** (`Step3ChunkMarkdown.py`) - Splits into searchable segments
4. **Extract Metadata** (`Step4MetaDataTags.py`) - Identifies companies, dates, report types
5. **Combine Data** (`Step5CombineMetaData.py`) - Consolidates all metadata
6. **Build Search Index** (`Step6CreateEmbeddings.py`) - Creates vector embeddings for AI search
7. **Start Backend Server** (`Step7MCPServerPsxGPT.py`) - Launches the data query server
8. **Launch Web Interface** (`Step8MCPClientPsxGPT.py`) - Starts the user-friendly chat interface

**Quality Assurance:** Use `Tool2ValidateProcessing.py` to verify data quality after processing.

## How to Get Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database
- API Keys:
  - [Google Gemini](https://ai.google.dev/) - for embeddings and AI analysis
  - [LlamaParse](https://docs.cloud.llamaindex.ai/llamacloud/getting_started/api_key) - for PDF processing (free tier: 3,000 pages)
  - [Anthropic](https://www.anthropic.com/) - for Claude AI integration
  - [Mistral](https://console.mistral.ai/) - for scanned document OCR

### Step 1: Install Code Editor (IDE)

Choose one of these beginner-friendly code editors:
- **[Windsurf](https://www.windsurf.io/)** (Recommended - AI-powered coding assistant)
- **[Cursor](https://cursor.sh/)** (AI-powered VS Code alternative)
- **[VS Code](https://code.visualstudio.com/)** (Popular free editor)

Download and install your chosen editor following the installer instructions.

### Step 2: Install Git

**For Windows Users:**
1. Visit [Git for Windows](https://git-scm.com/download/win)
2. Download the installer
3. Run the installer and follow the setup wizard
4. Use the default settings (recommended for beginners)
5. Git will be available in Command Prompt and PowerShell

**For Mac Users:**
1. Visit [Git for Mac](https://git-scm.com/download/mac)
2. Download the installer
3. Run the installer and follow the instructions
4. Alternatively, if you have Homebrew: `brew install git`
5. Git will be available in Terminal

### Step 3: Install Python

**For Windows Users:**
1. Visit [Python.org Downloads](https://www.python.org/downloads/windows/)
2. Download Python 3.11 or higher (click the yellow "Download Python" button)
3. Run the installer
4. **IMPORTANT**: Check the box "Add Python to PATH" during installation
   - This allows you to run Python commands from any folder in Command Prompt
   - Without this, Windows won't recognize Python commands
5. Click "Install Now"

**For Mac Users:**
1. Visit [Python.org Downloads](https://www.python.org/downloads/macos/)
2. Download Python 3.11 or higher
3. Run the installer and follow the instructions

### Step 4: Install PostgreSQL Database

**For Windows Users:**
1. Visit [PostgreSQL Downloads](https://www.postgresql.org/download/windows/)
2. Download the installer for Windows
3. Run the installer and follow the setup wizard
4. Remember the password you set for the "postgres" user

**For Mac Users:**
1. Visit [PostgreSQL Downloads](https://www.postgresql.org/download/macosx/)
2. Download the installer for macOS
3. Run the installer and follow the setup wizard
4. Remember the password you set for the "postgres" user

### Step 5: Install uv Package Manager

**For Windows Users:**
1. Open Command Prompt or PowerShell:
   - Press `Windows key + R`, type `cmd`, press Enter
   - OR Press `Windows key + X`, select "Windows PowerShell (Admin)"
2. Run this command:
   ```
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

**For Mac Users:**
1. Open Terminal:
   - Press `Command + Spacebar`, type "Terminal", press Enter
   - OR Go to Applications > Utilities > Terminal
2. Run this command:
   ```
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

### Step 6: Get Your API Keys

You'll need to sign up for these services and get API keys:

1. **[Google Gemini API](https://ai.google.dev/)** (Credit card required)
   - Click "Get API key in Google AI Studio"
   - Sign in with your Google account
   - Create a new API key
   - Copy the key

2. **[LlamaParse API](https://docs.cloud.llamaindex.ai/llamacloud/getting_started/api_key)**
   - Sign up for LlamaCloud
   - Go to API Keys section
   - Create a new API key
   - Copy the key (free tier includes 3,000 pages)

3. **[Anthropic API](https://www.anthropic.com/)** (Credit card required)
   - Sign up for an Anthropic account
   - Go to your dashboard
   - Create an API key
   - Copy the key

4. **[Mistral API](https://console.mistral.ai/)** (Credit card required, optional for scanned documents)
   - Sign up for Mistral AI
   - Go to API Keys
   - Create a new key
   - Copy the key

**Save these keys safely** - you'll paste them into your .env file in the next step.

### Step 7: Download and Setup psxGPT

```bash
git clone https://github.com/ishaheen10/psxgpt.git
cd psxgpt

# Setup environment
uv venv && source .venv/bin/activate  # Mac
uv venv && .venv\Scripts\activate     # Windows
uv sync
```

#### Configure API Keys
1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Open the `.env` file in your code editor and replace the placeholder values with your actual API keys:
   ```
   # API Keys for psxGPT
   GEMINI_API_KEY=your_actual_gemini_key_here
   ANTHROPIC_API_KEY=your_actual_anthropic_key_here
   LLAMA_CLOUD_API_KEY=your_actual_llama_cloud_key_here
   MISTRAL_API_KEY=your_actual_mistral_key_here
   
   # Database URLs (replace 'your_password' with your PostgreSQL password)
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/analyst_psx
   DATABASE_DIRECT_URL=postgresql://postgres:your_password@localhost:5432/analyst_psx
   ```

#### Configure Chainlit Settings
1. Open `.chainlit/config.toml` in your code editor
2. Update the database configuration if needed:
   ```toml
   [project]
   # Whether to enable telemetry (default: true). No personal data is collected.
   enable_telemetry = true
   
   # Duration (in seconds) during which the session is saved when the connection is lost
   session_timeout = 3600
   
   # Duration (in seconds) of the user session expiry
   user_session_timeout = 1296000  # 15 days
   ```

#### Setup Database
```bash
createdb analyst_psx
psql -d analyst_psx -f chainlit_schema_psx.sql
```

### Quick Start Options

**Option A: Use Existing Data (Fastest)**
If you have a `psx_bank_metadata` folder with processed financial data:
```bash
python Step6CreateEmbeddings.py
python Step8MCPClientPsxGPT.py
```
Access at http://localhost:8000 (Login: user@psx.com / user2024)

**Option B: Process Your Own PDFs**
To analyze your own financial documents:
```bash
# Option 1: Download from PSX (Pakistan Stock Exchange only)
python Step1DownloadPDFsSearch.py  # Downloads from PSX website
# OR modify script for other sources, or use browser-use for general purpose search

# Option 2: Place your own PDFs in psx_bank_reports/ folder, then run:
python Step2ConvertPDFtoMarkdown.py  # Uses LlamaParse or Tool1Mistral_OCR.py for scans
python Step3ChunkMarkdown.py
python Step4MetaDataTags.py
python Step5CombineMetaData.py
python Tool2ValidateProcessing.py   # Verify data quality
python Step6CreateEmbeddings.py
python Step8MCPClientPsxGPT.py
```

*Note: Step1 scripts are designed for PSX website. For other data sources, modify the download scripts or use a browser automation tool like browser-use.*

## Customization for Other Financial Data

To adapt psxGPT for different financial datasets:

1. **Replace Data Source**: Modify `Step1DownloadPDFsSearch.py` to point to your data source
2. **Update File Paths**: Change directory paths in scripts to match your folder structure
3. **Adjust Metadata Extraction**: Modify `Step4MetaDataTags.py` for your document types
4. **Configure OCR**: For scanned documents, ensure Mistral OCR is configured in `Step2ConvertPDFtoMarkdown.py`

## Troubleshooting

**Common Issues:**
- **Scanned PDFs**: Use Mistral OCR option in Step 2 for better text extraction
- **Large Files**: LlamaParse free tier has 3,000 page limit
- **Database Connection**: Verify PostgreSQL is running and credentials in `.env` are correct
- **API Limits**: Check API key quotas if processing fails

**Performance:**
- Processing time depends on document count and size
- Vector embedding creation (Step 6) is the most time-intensive step
- Consider processing documents in batches for large datasets

## Authentication

**Default Login Credentials:**
- **Username:** `user@psx.com`
- **Password:** `user2024`

*Note: These are demo credentials hardcoded for testing. For production use, implement proper authentication.*

## 📄 License

MIT License

Copyright (c) 2024 psxGPT Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.