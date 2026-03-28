import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from config import SECRET_KEY, VOICE_PROFILE, QUALITY_GATE, TIER_1_SOURCES, REJECTED_SOURCES
from scrapers.market_intel import gather_all_intel

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Simple file-based storage for drafts
DRAFTS_DIR = os.path.join(os.path.dirname(__file__), "data", "drafts")
os.makedirs(DRAFTS_DIR, exist_ok=True)


def build_linkedin_prompt(topic, raw_thoughts="", tone_adjustment="", num_variants=1):
    """Build a ready-to-paste prompt for Claude.ai."""
    prompt = f"""Generate {num_variants} LinkedIn post variant(s) based on the following input.

{VOICE_PROFILE}

TOPIC: {topic}
"""
    if raw_thoughts:
        prompt += f"\nRAW THOUGHTS / NOTES: {raw_thoughts}\n"
    if tone_adjustment:
        prompt += f"\nTONE ADJUSTMENT: {tone_adjustment}\n"

    prompt += f"""
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
    return prompt


def build_refine_prompt(original_draft, feedback):
    """Build a refinement prompt for Claude.ai."""
    return f"""Revise this LinkedIn post based on the feedback below. Maintain the same voice profile.

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


def build_digest_prompt(intel_data, custom_focus=""):
    """Build a digest generation prompt for Claude.ai."""
    prompt = f"""You are drafting a weekly market intelligence newsletter for Dallas Cullen's Substack.

{VOICE_PROFILE}

SOURCE FILTERING:
Only reference insights from tier-1 sources: {', '.join(TIER_1_SOURCES)}
Reject or flag anything from: {', '.join(REJECTED_SOURCES)}
Reject anything citing "experts say" without named sources.
Reject PR-driven announcements without independent verification.

RAW INTELLIGENCE DATA:
{intel_data}
"""
    if custom_focus:
        prompt += f"\nCUSTOM FOCUS AREA THIS WEEK: {custom_focus}\n"

    prompt += f"""
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
    return prompt


def build_digest_refine_prompt(original_digest, feedback):
    """Build a digest refinement prompt for Claude.ai."""
    return f"""Revise this newsletter digest based on the feedback below.

{VOICE_PROFILE}

ORIGINAL DIGEST:
{original_digest}

FEEDBACK / REVISION REQUEST:
{feedback}

Maintain Dallas's voice. Keep total length 600-900 words. Apply all quality gates:
{QUALITY_GATE}

Return the full revised newsletter.
"""


def save_draft(draft_type, content, metadata=None):
    """Save a draft to disk."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{draft_type}_{timestamp}.json"
    filepath = os.path.join(DRAFTS_DIR, filename)
    data = {
        "type": draft_type,
        "content": content,
        "metadata": metadata or {},
        "created_at": datetime.now().isoformat(),
        "status": "draft",
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filename


def load_drafts(draft_type=None):
    """Load all drafts, optionally filtered by type."""
    drafts = []
    if not os.path.exists(DRAFTS_DIR):
        return drafts
    for filename in sorted(os.listdir(DRAFTS_DIR), reverse=True):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(DRAFTS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            data["filename"] = filename
            if draft_type is None or data.get("type") == draft_type:
                drafts.append(data)
    return drafts


def load_draft(filename):
    """Load a single draft by filename."""
    filepath = os.path.join(DRAFTS_DIR, filename)
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        data["filename"] = filename
        return data


def delete_draft(filename):
    """Delete a draft file."""
    filepath = os.path.join(DRAFTS_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


# --- Routes ---

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/linkedin", methods=["GET", "POST"])
def linkedin():
    prompt = None
    if request.method == "POST":
        topic = request.form.get("topic", "").strip()
        raw_thoughts = request.form.get("raw_thoughts", "").strip()
        tone = request.form.get("tone_adjustment", "").strip()
        num_variants = int(request.form.get("num_variants", 1))

        if not topic:
            return render_template("linkedin.html", error="Please enter a topic.")

        prompt = build_linkedin_prompt(topic, raw_thoughts, tone, num_variants)

    return render_template("linkedin.html", prompt=prompt)


@app.route("/linkedin/refine", methods=["POST"])
def linkedin_refine():
    original = request.form.get("original_draft", "").strip()
    feedback = request.form.get("feedback", "").strip()

    if not original or not feedback:
        return render_template("linkedin.html", error="Need both the draft and your feedback.")

    prompt = build_refine_prompt(original, feedback)
    return render_template("linkedin.html", prompt=prompt, is_refine=True)


@app.route("/linkedin/save", methods=["POST"])
def linkedin_save():
    content = request.form.get("final_content", "").strip()
    topic = request.form.get("topic", "")
    if content:
        save_draft("linkedin", content, {"topic": topic})
        return render_template("linkedin.html", saved=True)
    return render_template("linkedin.html", error="Nothing to save — paste your final draft first.")


@app.route("/digest", methods=["GET", "POST"])
def digest():
    prompt = None
    intel_data = None

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "gather":
            try:
                intel_data = gather_all_intel()
            except Exception as e:
                return render_template("digest.html", error=f"Scraping error: {str(e)}")

        elif action == "generate":
            intel_data = request.form.get("intel_data", "").strip()
            manual_intel = request.form.get("manual_intel", "").strip()
            custom_focus = request.form.get("custom_focus", "").strip()

            combined_intel = intel_data
            if manual_intel:
                combined_intel += "\n\nMANUAL INTELLIGENCE ADDITIONS:\n" + manual_intel

            if not combined_intel.strip():
                return render_template("digest.html", error="No intelligence data. Gather feeds or paste manually.")

            prompt = build_digest_prompt(combined_intel, custom_focus)

        elif action == "refine":
            original = request.form.get("original_digest", "").strip()
            feedback = request.form.get("feedback", "").strip()
            if not original or not feedback:
                return render_template("digest.html", error="Need both the digest and your feedback.")
            prompt = build_digest_refine_prompt(original, feedback)

    return render_template("digest.html", prompt=prompt, intel_data=intel_data)


@app.route("/digest/save", methods=["POST"])
def digest_save():
    content = request.form.get("final_content", "").strip()
    focus = request.form.get("custom_focus", "")
    if content:
        save_draft("digest", content, {"custom_focus": focus})
        return render_template("digest.html", saved=True)
    return render_template("digest.html", error="Nothing to save — paste your final digest first.")


@app.route("/drafts")
def drafts():
    draft_type = request.args.get("type")
    all_drafts = load_drafts(draft_type)
    return render_template("drafts.html", drafts=all_drafts, filter_type=draft_type)


@app.route("/drafts/<filename>")
def view_draft(filename):
    draft = load_draft(filename)
    if not draft:
        return redirect(url_for("drafts"))
    return render_template("view_draft.html", draft=draft)


@app.route("/drafts/<filename>/delete", methods=["POST"])
def delete_draft_route(filename):
    delete_draft(filename)
    return redirect(url_for("drafts"))


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "mode": "free",
        "timestamp": datetime.now().isoformat(),
    })


if __name__ == "__main__":
    print("\n=== Thought Leadership Engine ===")
    print("Open http://localhost:5001 in your browser")
    print("==================================\n")
    app.run(debug=True, port=5001)
