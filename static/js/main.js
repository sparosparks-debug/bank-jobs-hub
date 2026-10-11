// Main UI interactions for Apex Banking Portal

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Menu Toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('show');
        });
    }

    // 2. FAQ Accordion Toggle
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        if (question) {
            question.addEventListener('click', () => {
                const isActive = item.classList.contains('active');
                faqItems.forEach(i => i.classList.remove('active'));
                if (!isActive) {
                    item.classList.add('active');
                }
            });
        }
    });

    // 3. Flash alert close buttons
    const closeFlashBtns = document.querySelectorAll('.close-flash');
    closeFlashBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const alert = e.target.closest('.flash-alert');
            if (alert) {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 250);
            }
        });
    });

    // 4. Bookmark Job Toggle (Works globally on cards)
    document.addEventListener('click', async (e) => {
        const btn = e.target.closest('.btn-bookmark');
        if (!btn) return;
        
        e.preventDefault();
        const jobId = btn.dataset.jobId;
        if (!jobId) return;

        try {
            const res = await fetch(`/api/save-job/${jobId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (res.status === 401) {
                window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`;
                return;
            }

            const data = await res.json();
            if (data.success) {
                if (data.saved) {
                    btn.classList.add('saved');
                    btn.setAttribute('title', 'Remove from saved jobs');
                    showToast('Job saved to your dashboard bookmarks.', 'success');
                } else {
                    btn.classList.remove('saved');
                    btn.setAttribute('title', 'Save to favorites');
                    showToast('Job removed from bookmarks.', 'info');
                }
            }
        } catch (err) {
            console.error('Bookmark error:', err);
        }
    });
});

// Toast notification helper
function showToast(message, type = 'info') {
    let toast = document.createElement('div');
    toast.className = `flash-alert ${type}`;
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.style.boxShadow = '0 10px 25px rgba(0,0,0,0.2)';
    toast.style.transition = 'all 0.3s ease';
    toast.innerHTML = `<span>${message}</span>`;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
