// Tab toggle helper
function setEditorTab(tab) {
    const writePane = document.getElementById('pane-write');
    const prevPane = document.getElementById('pane-preview');
    const btnWrite = document.getElementById('btn-tab-write');
    const btnPrev = document.getElementById('btn-tab-preview');
    const textVal = document.getElementById('description').value;

    if (tab === 'preview') {
        writePane.style.display = 'none';
        prevPane.style.display = 'block';
        btnWrite.classList.remove('is-active');
        btnPrev.classList.add('is-active');

        if (window.marked && window.DOMPurify) {
            const html = DOMPurify.sanitize(marked.parse(textVal || '*Nothing to preview yet.*'));
            document.getElementById('preview-content').innerHTML = html;
        }
    } else {
        writePane.style.display = 'block';
        prevPane.style.display = 'none';
        btnWrite.classList.add('is-active');
        btnPrev.classList.remove('is-active');
    }
}

// Insert markdown tags
function insertMd(prefix, suffix, defaultVal) {
    const ta = document.getElementById('description');
    if (!ta) return;
    setEditorTab('write');

    const start = ta.selectionStart;
    const end = ta.selectionEnd;
    const selected = ta.value.substring(start, end) || defaultVal;
    const replacement = prefix + selected + suffix;

    ta.value = ta.value.substring(0, start) + replacement + ta.value.substring(end);
    ta.focus();
    ta.setSelectionRange(start + prefix.length, start + prefix.length + selected.length);
}