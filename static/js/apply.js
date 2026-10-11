// Application Form Validation & Experience Helper

document.addEventListener('DOMContentLoaded', () => {
    const applyForm = document.getElementById('bankingApplicationForm');
    if (!applyForm) return;

    const resumeInput = document.getElementById('resume');
    const photoInput = document.getElementById('photo');
    const submitBtn = document.getElementById('submitAppBtn');
    const resumeHelp = document.getElementById('resumeHelp');

    if (resumeInput) {
        resumeInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;

            // Check extension
            const ext = file.name.split('.').pop().toLowerCase();
            if (ext !== 'pdf') {
                alert('Invalid file format. Please upload your resume in PDF format only (.pdf).');
                resumeInput.value = '';
                return;
            }

            // Check file size (max 8MB)
            if (file.size > 8 * 1024 * 1024) {
                alert('The selected PDF file exceeds the 8MB file size limit. Please choose a smaller file.');
                resumeInput.value = '';
                return;
            }

            if (resumeHelp) {
                resumeHelp.textContent = `Selected: ${file.name} (${(file.size / (1024 * 1024)).toFixed(2)} MB)`;
                resumeHelp.style.color = '#0d8253';
                resumeHelp.style.fontWeight = '600';
            }
        });
    }

    if (photoInput) {
        photoInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const allowed = ['jpg', 'jpeg', 'png', 'webp'];
            const ext = file.name.split('.').pop().toLowerCase();
            if (!allowed.includes(ext)) {
                alert('Invalid image format. Please upload JPG, PNG, or WEBP.');
                photoInput.value = '';
                return;
            }

            if (file.size > 4 * 1024 * 1024) {
                alert('Photograph size cannot exceed 4MB.');
                photoInput.value = '';
                return;
            }
        });
    }

    applyForm.addEventListener('submit', (e) => {
        const consentCheckbox = document.getElementById('consent');
        if (consentCheckbox && !consentCheckbox.checked) {
            e.preventDefault();
            alert('Please check and agree to the declaration statement before submitting.');
            return;
        }

        const mobile = document.getElementById('candidate_mobile');
        if (mobile && mobile.value.trim().length < 8) {
            e.preventDefault();
            alert('Please enter a valid mobile number with at least 8 digits.');
            mobile.focus();
            return;
        }

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
                <svg class="animate-spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation: spin 1s linear infinite;">
                    <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
                    <path d="M12 2a10 10 0 0 1 10 10" stroke-opacity="0.75"></path>
                </svg>
                Verifying & Submitting Application...
            `;
        }
    });
});
