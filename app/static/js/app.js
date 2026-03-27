// AG City - Minimal JS (HTMX handles most interactions)

// Show toast notifications from HTMX responses
document.body.addEventListener('showToast', function(evt) {
    const toast = document.createElement('div');
    toast.className = `alert alert-${evt.detail.type || 'success'} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    toast.style.zIndex = '9999';
    toast.innerHTML = `${evt.detail.message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
});

// Confirm delete actions
document.addEventListener('htmx:confirm', function(evt) {
    if (evt.detail.question) {
        evt.preventDefault();
        if (confirm(evt.detail.question)) {
            evt.detail.issueRequest();
        }
    }
});

// Auto-dismiss alerts after 5 seconds
document.querySelectorAll('.alert-dismissible').forEach(alert => {
    setTimeout(() => {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        if (bsAlert) bsAlert.close();
    }, 5000);
});
