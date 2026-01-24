/**
 * Admin Dashboard Shared Functions
 * Common Alpine.js utilities and helpers
 * 
 * Note: Core functions like authFetch, showAlert, and handleLogout
 * are defined in admin/base.html to ensure they're available on every page.
 * This file contains additional utility functions.
 */

// Date formatting helper
window.formatDate = function(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
};

// DateTime formatting helper
window.formatDateTime = function(dateString) {
    return new Date(dateString).toLocaleString('en-US');
};

// CSV export helper
window.exportToCSV = function(data, headers, filename = 'export.csv') {
    const csv = [headers, ...data].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
};
