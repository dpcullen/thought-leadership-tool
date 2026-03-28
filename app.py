import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from config import SECRET_KEY, ANTHROPIC_API_KEY
from generators.post_generator import generate_linkedin_post, refine_post
from generators.digest_generator import generate_digest, refine_digest
from scrapers.market_intel import gather_all_intel

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Simple file-based storage for drafts
DRAFTS_DIR = os.path.join(os.path.dirname(__file__), "data", "drafts")
os.makedirs(DRAFTS_DIR, exist_ok=True)


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


def update_draft(filename, updates):
    """Update a draft file."""
    filepath = os.path.join(DRAFTS_DIR, filename)
    if not os.path.exists(filepath):
        return False
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.update(updates)
    data["updated_at"] = datetime.now().isoformat()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return True


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
    result = None
    warnings = []
    if request.method == "POST":
        topic = request.form.get("topic", "").strip()
        raw_thoughts = request.form.get("raw_thoughts", "").strip()
        tone = request.form.get("tone_adjustment", "").strip()
        num_variants = int(request.form.get("num_variants", 1))

        if not topic:
            return render_template("linkedin.html", error="Please enter a topic.")

        try:
            result_data = generate_linkedin_post(topic, raw_thoughts, tone, num_variants)
            result = result_data["drafts"]
            warnings = result_data["warnings"]

            # Auto-save draft
            save_draft("linkedin", result, {
                "topic": topic,
                "raw_thoughts": raw_thoughts,
                "tone": tone,
            })
        except Exception as e:
            return render_template("linkedin.html", error=f"Generation error: {str(e)}")

    return render_template("linkedin.html", result=result, warnings=warnings)


@app.route("/linkedin/refine", methods=["POST"])
def linkedin_refine():
    original = request.form.get("original_draft", "").strip()
    feedback = request.form.get("feedback", "").strip()

    if not original or not feedback:
        return render_template("linkedin.html", error="Need both the draft and your feedback.")

    try:
        refined = refine_post(original, feedback)
        save_draft("linkedin", refined, {"feedback": feedback, "is_revision": True})
        return render_template("linkedin.html", result=refined, original=original, warnings=[])
    except Exception as e:
        return render_template("linkedin.html", error=f"Refinement error: {str(e)}")


@app.route("/digest", methods=["GET", "POST"])
def digest():
    result = None
    intel_data = None

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "gather":
            # Gather market intelligence
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
                return render_template("digest.html", error="No intelligence data to work with. Gather feeds or paste manually.")

            try:
                result = generate_digest(combined_intel, custom_focus)
                save_draft("digest", result, {"custom_focus": custom_focus})
            except Exception as e:
                return render_template("digest.html", error=f"Generation error: {str(e)}")

        elif action == "refine":
            original = request.form.get("original_digest", "").strip()
            feedback = request.form.get("feedback", "").strip()
            try:
                result = refine_digest(original, feedback)
                save_draft("digest", result, {"feedback": feedback, "is_revision": True})
            except Exception as e:
                return render_template("digest.html", error=f"Refinement error: {str(e)}")

    return render_template("digest.html", result=result, intel_data=intel_data)


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
        "api_key_configured": bool(ANTHROPIC_API_KEY),
        "timestamp": datetime.now().isoformat(),
    })


if __name__ == "__main__":
    print("\n=== Thought Leadership Tool ===")
    print("Open http://localhost:5000 in your browser")
    print("================================\n")
    app.run(debug=True, port=5000)
