// Filter feed posts
function filterPosts(type, btn) {
    const tabs = document.querySelectorAll('#feed-filter-tabs .bcet-tab-btn');
    tabs.forEach(t => t.classList.remove('is-active') || t.classList.add('google-glow-border'));
    if (btn) btn.classList.add('is-active') || btn.classList.remove('google-glow-border');

    const items = document.querySelectorAll('#bcet-posts-container .bcet-post-item');
    let visibleCount = 0;

    items.forEach(item => {
        const itemType = item.getAttribute('data-type');
        if (type === 'all' || itemType === type) {
            item.style.display = 'flex';
            visibleCount++;
        } else {
            item.style.display = 'none';
        }
    });

    const empty = document.getElementById('filter-empty-state');
    if (empty) {
        empty.style.display = (visibleCount === 0 && items.length > 0) ? 'block' : 'none';
    }
}

// Copy community link
function copyCommunityUrl(btn) {
    navigator.clipboard.writeText(window.location.href).then(() => {
        if (btn) {
            const orig = btn.innerHTML;
            btn.innerHTML = '<i data-lucide="check"></i> <span>Copied!</span>';
            if (window.lucide) lucide.createIcons();
            setTimeout(() => {
                btn.innerHTML = orig;
                if (window.lucide) lucide.createIcons();
            }, 2000);
        }
    });
}

// Copy post link
function copyPostUrl(btn, url) {
    navigator.clipboard.writeText(url).then(() => {
        if (btn) {
            const orig = btn.innerHTML;
            btn.innerHTML = '<i data-lucide="check"></i>';
            if (window.lucide) lucide.createIcons();
            setTimeout(() => {
                btn.innerHTML = orig;
                if (window.lucide) lucide.createIcons();
            }, 2000);
        }
    });
}