import anthropic
from config import VOICE_PROFILE, QUALITY_GATE, BANNED_WORDS, ANTHROPIC_API_KEY


def check_banned_words(text):
    """Check for banned words/phrases and return any found."""
    found = []
    lower_text = text.lower()
    for word in BANNED_WORDS:
        if word.lower() in lower_text:
            found.append(word)
    return found


def check_starts_with_i(text):
    """Check if post starts with 'I'."""
    stripped = text.strip()
    return stripped.startswith("I ") or stripped.startswith("I'")


def generate_linkedin_post(topic, raw_thoughts="", tone_adjustment="", num_variants=1):
    """Generate LinkedIn post(s) in Dallas's voice."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""Generate {num_variants} LinkedIn post variant(s) based on the following input.

{VOICE_PROFILE}

TOPIC: {topic}

{"RAW THOUGHTS / NOTES: " + raw_thoughts if raw_thoughts else ""}

{"TONE ADJUSTMENT: " + tone_adjustment if tone_adjustment else ""}

INSTRUCTIONS:
1. Write the post(s) following ALL voice and format rules above exactly.
2. Each post should be 150-250 words, prose only, no bullets.
3. Lead with the sharpest insight, not background.
4. After drafting, apply this quality gate:
{QUALITY_GATE}
5. If any quality gate fails, rewrite until it passes.
6. Do NOT start any post with the word "I".
7. Do NOT include any hashtags unless you can justify exactly why that specific hashtag adds value.
8. Return each variant clearly labeled (Variant 1, Variant 2, etc.)
9. After each variant, include a brief "Quality Gate Notes" section explaining how it passes each test.
"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text

    # Post-processing check
    warnings = []
    banned_found = check_banned_words(response_text)
    if banned_found:
        warnings.append(f"Banned words detected: {', '.join(banned_found)}")
    if check_starts_with_i(response_text):
        warnings.append("Post starts with 'I' — consider rewriting the opening")

    return {
        "drafts": response_text,
        "warnings": warnings,
        "word_count_note": "Target: 150-250 words per post"
    }


def refine_post(original_draft, feedback):
    """Refine a post based on user feedback while maintaining voice."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""Revise this LinkedIn post based on the feedback below. Maintain the same voice profile.

{VOICE_PROFILE}

ORIGINAL DRAFT:
{original_draft}

FEEDBACK / REVISION REQUEST:
{feedback}

INSTRUCTIONS:
1. Apply the feedback while keeping the voice consistent.
2. Ensure the revised post still passes all quality gates:
{QUALITY_GATE}
3. Keep it 150-250 words, prose only, no bullets.
4. Do NOT start with "I".
5. Return the revised post and brief notes on what changed.
"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text
