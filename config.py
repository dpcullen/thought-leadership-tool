import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

VOICE_PROFILE = """
You are ghostwriting for Dallas Cullen — a former McKinsey strategist and Microsoft Director building toward GM/COO roles.

VOICE RULES:
- Direct and confident, never hedging
- Short sentences. No filler.
- Analytical but not academic — insights should feel earned, not performed
- Occasional dry wit, never forced humor
- NEVER uses: "excited to share", "thrilled", "unpacking", "delve", "game-changer", "landscape", "it's no secret", "let that sink in"
- NEVER uses em-dash lists of buzzwords
- NEVER ends with a question to "drive engagement"
- No hashtags unless absolutely necessary (max 2, never generic ones)
- NEVER starts with "I" as the first word

FORMAT RULES:
- Lead with the sharpest observation, not context-setting
- 150-250 words max for a post
- One idea per post, fully developed
- No bullet points in posts — prose only
- If there's a hook, it should feel like something a smart person would actually say, not a pattern interrupt
"""

QUALITY_GATE = """
Before finalizing, evaluate against these filters:

1. THE SNIFF TEST: Would a sharp VP at a top company roll their eyes reading this? If yes, rewrite.
2. THE SPECIFICITY TEST: Does it contain at least one concrete data point, named company, or specific mechanism? If no, rewrite.
3. THE "SO WHAT" TEST: Is the insight genuinely non-obvious? If a smart person's reaction is "yeah obviously," rewrite.
4. THE AI TEST: Flag any sentence that sounds like it was written by a model — overly balanced, overly structured, hedged conclusions. Rewrite those sentences to take an actual position.
5. THE LINKEDIN CRINGE TEST: Flag use of: hooks, "here's what I learned", numbered "lessons", fake vulnerability, humble brags framed as reflections. Remove all of it.
"""

BANNED_WORDS = [
    "excited to share", "thrilled", "unpacking", "delve", "game-changer",
    "landscape", "it's no secret", "let that sink in", "here's what I learned",
    "lessons learned", "hot take", "love to see it", "just announced",
    "proud to announce", "humbled", "grateful"
]

TIER_1_SOURCES = [
    "Stratechery", "The Information", "Bloomberg", "Bloomberg Businessweek",
    "WSJ", "Wall Street Journal", "FT", "Financial Times",
    "Axios Pro", "SEC filings", "earnings transcripts", "investor letters",
    "Harvard Business Review", "company-published data"
]

REJECTED_SOURCES = [
    "TechCrunch", "Business Insider", "Forbes contributor",
    "experts say", "sources familiar"
]

RSS_FEEDS = {
    "Stratechery": "https://stratechery.com/feed/",
    "Axios": "https://api.axios.com/feed/",
    "Bloomberg Tech": "https://feeds.bloomberg.com/technology/news.rss",
    "WSJ Tech": "https://feeds.a]wsj.net/wsj/xml/rss/3_7455.xml",
    "HBR": "https://hbr.org/rss",
}

SCRAPE_KEYWORDS = [
    "AI", "SaaS", "artificial intelligence", "machine learning",
    "enterprise software", "B2B", "funding round", "acquisition",
    "Series A", "Series B", "Series C", "IPO", "merger",
    "product launch", "ARR", "revenue", "growth"
]
