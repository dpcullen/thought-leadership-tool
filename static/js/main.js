// Copy to clipboard
function copyToClipboard(elementId) {
    const el = document.getElementById(elementId);
    if (!el) return;

    const text = el.innerText || el.textContent;
    navigator.clipboard.writeText(text).then(() => {
        const btn = el.parentElement.querySelector('.copy-btn');
        if (btn) {
            const originalText = btn.textContent;
            btn.textContent = 'Copied!';
            setTimeout(() => { btn.textContent = originalText; }, 2000);
        }
    });
}

// Show loading state on form submit
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[data-loading]');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const loadingId = form.getAttribute('data-loading');
            const loading = document.getElementById(loadingId);
            if (loading) loading.classList.add('active');

            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Generating...';
            }
        });
    });

    // Health check
    fetch('/api/health')
        .then(r => r.json())
        .then(data => {
            const dot = document.querySelector('.status-dot');
            if (dot) {
                dot.classList.toggle('error', !data.api_key_configured);
            }
            const statusText = document.querySelector('.status-text');
            if (statusText) {
                statusText.textContent = data.api_key_configured
                    ? 'API connected'
                    : 'API key not configured — add ANTHROPIC_API_KEY to .env';
            }
        })
        .catch(() => {
            const dot = document.querySelector('.status-dot');
            if (dot) dot.classList.add('error');
        });
});

// Word count for textareas
function updateWordCount(textareaId, countId) {
    const textarea = document.getElementById(textareaId);
    const counter = document.getElementById(countId);
    if (!textarea || !counter) return;

    textarea.addEventListener('input', function() {
        const words = this.value.trim().split(/\s+/).filter(w => w.length > 0).length;
        counter.textContent = words + ' words';
    });
}
