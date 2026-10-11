// Jobs dynamic filtering, searching, and asynchronous card rendering

document.addEventListener('DOMContentLoaded', () => {
    const filterForm = document.getElementById('jobFiltersForm');
    const jobsGrid = document.getElementById('jobsGridContainer');
    const resultsCountEl = document.getElementById('resultsCount');
    const resetBtn = document.getElementById('resetFiltersBtn');

    if (!filterForm || !jobsGrid) return;

    let debounceTimer;

    function fetchAndRenderJobs() {
        const formData = new FormData(filterForm);
        const params = new URLSearchParams(formData);

        // Visual loading state
        jobsGrid.style.opacity = '0.5';

        fetch(`/api/jobs?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                jobsGrid.style.opacity = '1';
                if (!data.success) return;

                if (resultsCountEl) {
                    resultsCountEl.textContent = `${data.count} Vacanc${data.count === 1 ? 'y' : 'ies'} Found`;
                }

                if (data.jobs.length === 0) {
                    jobsGrid.innerHTML = `
                        <div style="grid-column: 1/-1; text-align: center; padding: 4rem 1rem; background: #fff; border-radius: 16px; border: 1px dashed #cbd5e1;">
                            <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5" style="margin-bottom: 1rem;">
                                <circle cx="11" cy="11" r="8"></circle>
                                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                            </svg>
                            <h3 style="color: #0f172a; margin-bottom: 0.5rem; font-weight: 700;">No matching banking vacancies found</h3>
                            <p style="color: #64748b; max-width: 450px; margin: 0 auto 1.5rem;">Try modifying your keyword, selecting a different bank category or adjusting experience level filters.</p>
                            <button id="inlineResetBtn" class="btn btn-outline" style="font-size: 0.88rem;">Reset All Filters</button>
                        </div>
                    `;
                    const inlineBtn = document.getElementById('inlineResetBtn');
                    if (inlineBtn) {
                        inlineBtn.addEventListener('click', resetFilters);
                    }
                    return;
                }

                jobsGrid.innerHTML = data.jobs.map(job => renderJobCard(job)).join('');
            })
            .catch(err => {
                jobsGrid.style.opacity = '1';
                console.error('Error fetching jobs:', err);
            });
    }

    function renderJobCard(job) {
        const isGovt = job.bank_type === 'Government';
        const typeClass = isGovt ? 'govt' : 'private';
        const bankInitial = job.bank_name ? job.bank_name.charAt(0) : 'B';
        const isSaved = job.is_saved ? 'saved' : '';
        const savedTitle = job.is_saved ? 'Remove from saved jobs' : 'Save to favorites';

        let officialOrApply = '';
        if (isGovt && job.official_notification_url) {
            officialOrApply = `
                <a href="${job.official_notification_url}" target="_blank" rel="noopener noreferrer" class="btn btn-outline btn-sm" title="View official government recruitment notice">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                    Notification
                </a>
            `;
        } else if (!isGovt && job.employer_apply_url) {
            officialOrApply = `
                <a href="${job.employer_apply_url}" target="_blank" rel="noopener noreferrer" class="btn btn-outline btn-sm" title="View employer website">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
                    Employer Site
                </a>
            `;
        }

        let applyAction = '';
        if (job.has_applied) {
            applyAction = `<span class="status-pill Submitted">Applied</span>`;
        } else {
            applyAction = `<a href="/apply/${job.job_id}" class="btn btn-primary btn-sm">Apply Now</a>`;
        }

        return `
            <div class="job-card">
                <div>
                    <div class="job-card-header">
                        <div class="bank-meta">
                            <div class="bank-avatar">${bankInitial}</div>
                            <div class="bank-info">
                                <h4>${job.bank_name}</h4>
                                <span class="bank-type-badge ${typeClass}">${job.bank_type} Bank</span>
                            </div>
                        </div>
                        <div style="display:flex; flex-direction:column; align-items:flex-end; gap:4px;">
                            ${job.is_sample_data ? '<span class="sample-badge">Sample Listing</span>' : ''}
                            <button class="btn-bookmark ${isSaved}" data-job-id="${job.job_id}" title="${savedTitle}">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2">
                                    <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                                </svg>
                            </button>
                        </div>
                    </div>

                    <a href="/jobs/${job.job_id}" class="job-title-link">${job.job_title}</a>
                    <p class="job-snippet">${job.job_description}</p>

                    <div class="job-specs-list">
                        <span class="job-spec-item">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                            ${job.location}
                        </span>
                        <span class="job-spec-item">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                            ${job.salary_range}
                        </span>
                        <span class="job-spec-item">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>
                            ${job.experience_level}
                        </span>
                        <span class="job-spec-item">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
                            ${job.category}
                        </span>
                    </div>
                </div>

                <div class="job-card-footer">
                    <div class="deadline-info">
                        Deadline: <strong>${job.application_deadline}</strong>
                    </div>
                    <div class="card-actions">
                        ${officialOrApply}
                        ${applyAction}
                    </div>
                </div>
            </div>
        `;
    }

    function resetFilters(e) {
        if (e) e.preventDefault();
        filterForm.reset();
        fetchAndRenderJobs();
    }

    // Event listeners for instant live updates
    filterForm.querySelectorAll('select').forEach(select => {
        select.addEventListener('change', fetchAndRenderJobs);
    });

    const keywordInput = filterForm.querySelector('input[name="keyword"]');
    if (keywordInput) {
        keywordInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(fetchAndRenderJobs, 350);
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', resetFilters);
    }
});
