import anthropic
from config import VOICE_PROFILE, QUALITY_GATE, TIER_1_SOURCES, REJECTED_SOURCES, ANTHROPIC_API_KEY


def generate_digest(intel_data, custom_focus=""):
    """Generate a weekly market intelligence digest / newsletter."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""You are drafting a weekly market intelligence newsletter for Dallas Cullen's Substack.

{VOICE_PROFILE}

SOURCE FILTERING:
Only reference insights from tier-1 sources: {', '.join(TIER_1_SOURCES)}
Reject or flag anything from: {', '.join(REJECTED_SOURCES)}
Reject anything citing "experts say" without named sources.
Reject PR-driven announcements without independent verification.

RAW INTELLIGENCE DATA:
{intel_data}

{"CUSTOM FOCUS AREA THIS WEEK: " + custom_focus if custom_focus else ""}

NEWSLETTER STRUCTURE:
1. HEADLINE INSIGHT (1 paragraph) — The single most important thing that happened this week in AI/SaaS. Lead with the "so what," not the "what happened."

2. DEAL FLOW (2-3 items) — Funding rounds, acquisitions, or M&A moves worth noting. For each: what happened, why it matters, what it signals about the market. Brief prose paragraphs, not bullets.

3. PRODUCT & STRATEGY MOVES (2-3 items) — Notable product launches, pivots, or strategic shifts. Focus on what the move reveals about where the market is heading.

4. THE NUMBER (1 item) — One specific data point from the week that tells a bigger story. A revenue figure, growth rate, market size estimate, or adoption metric. Explain why it matters in 2-3 sentences.

5. WHAT I'M WATCHING (1 paragraph) — One emerging trend or question Dallas is tracking. This should feel like genuine intellectual curiosity, not a forced prediction.

RULES:
- Total newsletter: 600-900 words
- Every section should pass the quality gates:
{QUALITY_GATE}
- Write in Dallas's voice throughout
- Never use "this week in tech" or similar generic framing
- Each item must reference a specific company, number, or named source
- Do NOT start any section with "I" or "This week"
- Cite sources inline (e.g., "per Bloomberg" or "according to the S-1")
"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def refine_digest(original_digest, feedback):
    """Refine a digest based on user feedback."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""Revise this newsletter digest based on the feedback below.

{VOICE_PROFILE}

ORIGINAL DIGEST:
{original_digest}

FEEDBACK / REVISION REQUEST:
{feedback}

Maintain Dallas's voice. Keep total length 600-900 words. Apply all quality gates:
{QUALITY_GATE}

Return the full revised newsletter.
"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text
