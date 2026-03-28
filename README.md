# Thought Leadership Engine

Ghostwriting tool for Dallas Cullen — generates LinkedIn posts and weekly market intelligence digests in a trained voice profile. Nothing publishes without explicit approval.

## Features

- **LinkedIn Post Generator** — Feed a topic or raw thoughts, get a polished draft (150-250 words) with quality gates applied
- **Weekly Market Digest** — Auto-gathers AI/SaaS intel from tier-1 RSS feeds, generates a Substack-ready newsletter (600-900 words)
- **Draft Library** — All generated content auto-saves for review, refinement, or deletion
- **Voice Profile** — Trained on direct, analytical style with zero LinkedIn cringe
- **Quality Gates** — Every draft passes sniff test, specificity test, "so what" test, AI detection, and LinkedIn cringe filters
- **Source Filtering** — Only tier-1 sources (Stratechery, Bloomberg, WSJ, FT, Axios Pro, SEC filings, HBR)

## Setup

### 1. Install Python dependencies

```bash
cd thought-leadership-tool
pip install -r requirements.txt
```

### 2. Configure API key

Copy the example env file and add your Anthropic API key:

```bash
cp .env.example .env
```

Edit `.env` and set:
```
ANTHROPIC_API_KEY=your-api-key-here
SECRET_KEY=any-random-string-here
```

Get an API key at https://console.anthropic.com/

### 3. Run the app

```bash
python app.py
```

Open http://localhost:5000 in your browser.

## Usage

### LinkedIn Posts
1. Go to **LinkedIn Posts** tab
2. Enter a topic and optional raw thoughts
3. Choose number of variants (1-3)
4. Review the generated draft
5. Refine with feedback or copy the final version

### Weekly Digest
1. Go to **Weekly Digest** tab
2. Click **Gather from Feeds** to pull RSS intel, or paste your own research
3. Optionally add a focus area for the week
4. Generate the newsletter draft
5. Refine or copy for Substack

### Saved Drafts
All generated content auto-saves. Filter by type, review, or delete from the **Saved Drafts** tab.
