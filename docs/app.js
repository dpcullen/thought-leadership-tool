// ============================================================
// Thought Leadership Engine — Static JS
// All prompt-building logic ported from config.py + app.py
// ============================================================

// --- Voice Profile & Config (from config.py) ---

const VOICE_PROFILE = `You are ghostwriting for Dallas Cullen — a former McKinsey strategist and Microsoft Director building toward GM/COO roles.

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
- If there's a hook, it should feel like something a smart person would actually say, not a pattern interrupt`;

const QUALITY_GATE = `Before finalizing, evaluate against these filters:

1. THE SNIFF TEST: Would a sharp VP at a top company roll their eyes reading this? If yes, rewrite.
2. THE SPECIFICITY TEST: Does it contain at least one concrete data point, named company, or specific mechanism? If no, rewrite.
3. THE "SO WHAT" TEST: Is the insight genuinely non-obvious? If a smart person's reaction is "yeah obviously," rewrite.
4. THE AI TEST: Flag any sentence that sounds like it was written by a model — overly balanced, overly structured, hedged conclusions. Rewrite those sentences to take an actual position.
5. THE LINKEDIN CRINGE TEST: Flag use of: hooks, "here's what I learned", numbered "lessons", fake vulnerability, humble brags framed as reflections. Remove all of it.`;

const BANNED_WORDS = [
    "excited to share", "thrilled", "unpacking", "delve", "game-changer",
    "landscape", "it's no secret", "let that sink in", "here's what I learned",
    "lessons learned", "hot take", "love to see it", "just announced",
    "proud to announce", "humbled", "grateful"
];

const TIER_1_SOURCES = [
    "Stratechery", "The Information", "Bloomberg", "Bloomberg Businessweek",
    "WSJ", "Wall Street Journal", "FT", "Financial Times",
    "Axios Pro", "SEC filings", "earnings transcripts", "investor letters",
    "Harvard Business Review", "company-published data"
];

const REJECTED_SOURCES = [
    "TechCrunch", "Business Insider", "Forbes contributor",
    "experts say", "sources familiar"
];


// --- Prompt Builders (ported from app.py) ---

function buildLinkedInPrompt(topic, rawThoughts, toneAdjustment, numVariants) {
    let prompt = `Generate ${numVariants} LinkedIn post variant(s) based on the following input.

${VOICE_PROFILE}

TOPIC: ${topic}
`;

    if (rawThoughts) {
        prompt += `\nRAW THOUGHTS / NOTES: ${rawThoughts}\n`;
    }
    if (toneAdjustment) {
        prompt += `\nTONE ADJUSTMENT: ${toneAdjustment}\n`;
    }

    prompt += `
INSTRUCTIONS:
1. Write the post(s) following ALL voice and format rules above exactly.
2. Each post should be 150-250 words, prose only, no bullets.
3. Lead with the sharpest insight, not background.
4. After drafting, apply this quality gate:
${QUALITY_GATE}
5. If any quality gate fails, rewrite until it passes.
6. Do NOT start any post with the word "I".
7. Do NOT include any hashtags unless you can justify exactly why that specific hashtag adds value.
8. Return each variant clearly labeled (Variant 1, Variant 2, etc.)
9. After each variant, include a brief "Quality Gate Notes" section explaining how it passes each test.
`;

    return prompt;
}

function buildRefinePrompt(originalDraft, feedback) {
    return `Revise this LinkedIn post based on the feedback below. Maintain the same voice profile.

${VOICE_PROFILE}

ORIGINAL DRAFT:
${originalDraft}

FEEDBACK / REVISION REQUEST:
${feedback}

INSTRUCTIONS:
1. Apply the feedback while keeping the voice consistent.
2. Ensure the revised post still passes all quality gates:
${QUALITY_GATE}
3. Keep it 150-250 words, prose only, no bullets.
4. Do NOT start with "I".
5. Return the revised post and brief notes on what changed.
`;
}

function buildDigestPrompt(intelData, customFocus) {
    let prompt = `You are drafting a weekly market intelligence newsletter for Dallas Cullen's Substack.

${VOICE_PROFILE}

SOURCE FILTERING:
Only reference insights from tier-1 sources: ${TIER_1_SOURCES.join(', ')}
Reject or flag anything from: ${REJECTED_SOURCES.join(', ')}
Reject anything citing "experts say" without named sources.
Reject PR-driven announcements without independent verification.

RAW INTELLIGENCE DATA:
${intelData}
`;

    if (customFocus) {
        prompt += `\nCUSTOM FOCUS AREA THIS WEEK: ${customFocus}\n`;
    }

    prompt += `
NEWSLETTER STRUCTURE:
1. HEADLINE INSIGHT (1 paragraph) — The single most important thing that happened this week in AI/SaaS. Lead with the "so what," not the "what happened."

2. DEAL FLOW (2-3 items) — Funding rounds, acquisitions, or M&A moves worth noting. For each: what happened, why it matters, what it signals about the market. Brief prose paragraphs, not bullets.

3. PRODUCT & STRATEGY MOVES (2-3 items) — Notable product launches, pivots, or strategic shifts. Focus on what the move reveals about where the market is heading.

4. THE NUMBER (1 item) — One specific data point from the week that tells a bigger story. A revenue figure, growth rate, market size estimate, or adoption metric. Explain why it matters in 2-3 sentences.

5. WHAT I'M WATCHING (1 paragraph) — One emerging trend or question Dallas is tracking. This should feel like genuine intellectual curiosity, not a forced prediction.

RULES:
- Total newsletter: 600-900 words
- Every section should pass the quality gates:
${QUALITY_GATE}
- Write in Dallas's voice throughout
- Never use "this week in tech" or similar generic framing
- Each item must reference a specific company, number, or named source
- Do NOT start any section with "I" or "This week"
- Cite sources inline (e.g., "per Bloomberg" or "according to the S-1")
`;

    return prompt;
}

function buildDigestRefinePrompt(originalDigest, feedback) {
    return `Revise this newsletter digest based on the feedback below.

${VOICE_PROFILE}

ORIGINAL DIGEST:
${originalDigest}

FEEDBACK / REVISION REQUEST:
${feedback}

Maintain Dallas's voice. Keep total length 600-900 words. Apply all quality gates:
${QUALITY_GATE}

Return the full revised newsletter.
`;
}


// --- Tab Navigation ---

function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(el => {
        el.classList.remove('active');
    });

    // Show selected tab
    const tab = document.getElementById('tab-' + tabName);
    if (tab) {
        tab.classList.add('active');
    }

    // Update nav links
    document.querySelectorAll('.nav-links a[data-tab]').forEach(el => {
        el.classList.remove('active');
    });
    const navLink = document.querySelector(`.nav-links a[data-tab="${tabName}"]`);
    if (navLink) {
        navLink.classList.add('active');
    }

    // Close mobile menu
    document.querySelector('.nav-links').classList.remove('open');

    // Refresh drafts when switching to drafts tab
    if (tabName === 'drafts') {
        renderDrafts();
    }

    // Scroll to top
    window.scrollTo(0, 0);
}

function toggleMobileMenu() {
    document.querySelector('.nav-links').classList.toggle('open');
}


// --- LinkedIn Post Generator ---

function generateLinkedInPrompt() {
    const topic = document.getElementById('li-topic').value.trim();
    const thoughts = document.getElementById('li-thoughts').value.trim();
    const tone = document.getElementById('li-tone').value.trim();
    const variants = document.getElementById('li-variants').value;

    if (!topic) {
        showAlert('li-save-msg', 'Please enter a topic.', 'error');
        document.getElementById('li-topic').focus();
        return;
    }

    const prompt = buildLinkedInPrompt(topic, thoughts, tone, parseInt(variants));

    document.getElementById('li-prompt-output').textContent = prompt;
    document.getElementById('li-prompt-section').style.display = 'block';

    // Scroll to the prompt
    document.getElementById('li-prompt-section').scrollIntoView({ behavior: 'smooth' });
}

function generateLinkedInRefinePrompt() {
    const draft = document.getElementById('li-refine-draft').value.trim();
    const feedback = document.getElementById('li-refine-feedback').value.trim();

    if (!draft || !feedback) {
        showAlert('li-save-msg', 'Please provide both the draft and your feedback.', 'error');
        return;
    }

    const prompt = buildRefinePrompt(draft, feedback);

    document.getElementById('li-refine-output').textContent = prompt;
    document.getElementById('li-refine-section').style.display = 'block';
    document.getElementById('li-refine-section').scrollIntoView({ behavior: 'smooth' });
}

function saveLinkedInDraft() {
    const content = document.getElementById('li-result').value.trim();
    const topic = document.getElementById('li-topic').value.trim();

    if (!content) {
        showAlert('li-save-msg', 'Please paste Claude\'s response first.', 'error');
        return;
    }

    saveDraft('linkedin', content, { topic: topic });
    document.getElementById('li-result').value = '';
    showAlert('li-save-msg', 'Draft saved! View it in the Saved Drafts tab.', 'success');
}


// --- Digest Builder ---

function generateDigestPrompt() {
    const intel = document.getElementById('dg-intel').value.trim();
    const focus = document.getElementById('dg-focus').value.trim();

    if (!intel) {
        showAlert('dg-save-msg', 'Please paste your research / intelligence data.', 'error');
        document.getElementById('dg-intel').focus();
        return;
    }

    const prompt = buildDigestPrompt(intel, focus);

    document.getElementById('dg-prompt-output').textContent = prompt;
    document.getElementById('dg-prompt-section').style.display = 'block';
    document.getElementById('dg-prompt-section').scrollIntoView({ behavior: 'smooth' });
}

function generateDigestRefinePrompt() {
    const draft = document.getElementById('dg-refine-draft').value.trim();
    const feedback = document.getElementById('dg-refine-feedback').value.trim();

    if (!draft || !feedback) {
        showAlert('dg-save-msg', 'Please provide both the digest and your feedback.', 'error');
        return;
    }

    const prompt = buildDigestRefinePrompt(draft, feedback);

    document.getElementById('dg-refine-output').textContent = prompt;
    document.getElementById('dg-refine-section').style.display = 'block';
    document.getElementById('dg-refine-section').scrollIntoView({ behavior: 'smooth' });
}

function saveDigestDraft() {
    const content = document.getElementById('dg-result').value.trim();
    const focus = document.getElementById('dg-focus').value.trim();

    if (!content) {
        showAlert('dg-save-msg', 'Please paste Claude\'s response first.', 'error');
        return;
    }

    saveDraft('digest', content, { custom_focus: focus });
    document.getElementById('dg-result').value = '';
    showAlert('dg-save-msg', 'Digest saved! View it in the Saved Drafts tab.', 'success');
}


// --- Copy to Clipboard ---

function copyPrompt(elementId, buttonEl) {
    const el = document.getElementById(elementId);
    const text = el.textContent || el.innerText;

    navigator.clipboard.writeText(text).then(() => {
        // Visual feedback
        const originalText = buttonEl.textContent;
        buttonEl.textContent = 'Copied!';
        buttonEl.classList.add('copied');

        setTimeout(() => {
            buttonEl.textContent = originalText;
            buttonEl.classList.remove('copied');
        }, 2000);
    }).catch(() => {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);

        const originalText = buttonEl.textContent;
        buttonEl.textContent = 'Copied!';
        buttonEl.classList.add('copied');

        setTimeout(() => {
            buttonEl.textContent = originalText;
            buttonEl.classList.remove('copied');
        }, 2000);
    });
}


// --- localStorage Draft Management ---

function getDrafts() {
    try {
        const data = localStorage.getItem('tl-drafts');
        return data ? JSON.parse(data) : [];
    } catch (e) {
        return [];
    }
}

function setDrafts(drafts) {
    localStorage.setItem('tl-drafts', JSON.stringify(drafts));
}

function saveDraft(type, content, metadata) {
    const drafts = getDrafts();
    const draft = {
        id: Date.now().toString(),
        type: type,
        content: content,
        metadata: metadata || {},
        created_at: new Date().toISOString(),
    };
    drafts.unshift(draft); // newest first
    setDrafts(drafts);
    return draft;
}

function deleteDraft(id) {
    let drafts = getDrafts();
    drafts = drafts.filter(d => d.id !== id);
    setDrafts(drafts);
}


// --- Render Drafts ---

let currentDraftFilter = 'all';

function filterDrafts(filterType, buttonEl) {
    currentDraftFilter = filterType;

    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    if (buttonEl) {
        buttonEl.classList.add('active');
    }

    renderDrafts();
}

function renderDrafts() {
    const container = document.getElementById('drafts-list');
    let drafts = getDrafts();

    if (currentDraftFilter !== 'all') {
        drafts = drafts.filter(d => d.type === currentDraftFilter);
    }

    if (drafts.length === 0) {
        container.innerHTML = '<p class="empty-state">No saved drafts yet. Generate a post or digest and save it here.</p>';
        return;
    }

    let html = '';
    drafts.forEach(draft => {
        const date = new Date(draft.created_at);
        const dateStr = date.toLocaleDateString('en-US', {
            month: 'short', day: 'numeric', year: 'numeric',
            hour: 'numeric', minute: '2-digit'
        });

        const badgeClass = draft.type === 'linkedin' ? 'badge-linkedin' : 'badge-digest';
        const badgeLabel = draft.type === 'linkedin' ? 'LinkedIn' : 'Digest';
        const preview = draft.content.substring(0, 150) + (draft.content.length > 150 ? '...' : '');
        const topicInfo = draft.metadata && draft.metadata.topic ? ` — ${draft.metadata.topic}` : '';
        const focusInfo = draft.metadata && draft.metadata.custom_focus ? ` — ${draft.metadata.custom_focus}` : '';

        html += `
            <div class="draft-item" onclick="viewDraft('${draft.id}')">
                <div class="draft-info">
                    <div><span class="badge ${badgeClass}">${badgeLabel}</span>${topicInfo}${focusInfo}</div>
                    <div class="date">${dateStr}</div>
                    <div class="preview">${escapeHtml(preview)}</div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}


// --- Draft Modal ---

function viewDraft(id) {
    const drafts = getDrafts();
    const draft = drafts.find(d => d.id === id);
    if (!draft) return;

    const date = new Date(draft.created_at);
    const dateStr = date.toLocaleDateString('en-US', {
        weekday: 'long', month: 'long', day: 'numeric', year: 'numeric',
        hour: 'numeric', minute: '2-digit'
    });

    const typeLabel = draft.type === 'linkedin' ? 'LinkedIn Post' : 'Weekly Digest';
    const topicInfo = draft.metadata && draft.metadata.topic ? `Topic: ${draft.metadata.topic}` : '';
    const focusInfo = draft.metadata && draft.metadata.custom_focus ? `Focus: ${draft.metadata.custom_focus}` : '';

    document.getElementById('modal-title').textContent = typeLabel;
    document.getElementById('modal-meta').textContent = [dateStr, topicInfo, focusInfo].filter(Boolean).join(' | ');
    document.getElementById('modal-body').textContent = draft.content;

    // Wire up delete button
    const deleteBtn = document.getElementById('modal-delete-btn');
    deleteBtn.onclick = function() {
        if (confirm('Delete this draft? This cannot be undone.')) {
            deleteDraft(id);
            closeModal();
            renderDrafts();
        }
    };

    document.getElementById('draft-modal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('draft-modal').style.display = 'none';
}

// Close modal on backdrop click
document.addEventListener('click', function(e) {
    if (e.target.id === 'draft-modal') {
        closeModal();
    }
});

// Close modal on Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});


// --- Utility ---

function showAlert(containerId, message, type) {
    const container = document.getElementById(containerId);
    container.innerHTML = `<div class="${type}">${escapeHtml(message)}</div>`;

    // Auto-clear after 5 seconds
    setTimeout(() => {
        container.innerHTML = '';
    }, 5000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
