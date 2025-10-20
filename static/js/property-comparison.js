/**
 * Property Comparison System
 * Traca Management Services
 */

// Storage key for comparison list
const COMPARISON_KEY = 'traca_property_comparison';
const MAX_COMPARISON = 3; // Maximum 3 properties to compare

// Initialize comparison system
document.addEventListener('DOMContentLoaded', function() {
    updateComparisonBadge();
    updateComparisonButtons();
});

// Get comparison list from localStorage
function getComparisonList() {
    const stored = localStorage.getItem(COMPARISON_KEY);
    return stored ? JSON.parse(stored) : [];
}

// Save comparison list to localStorage
function saveComparisonList(list) {
    localStorage.setItem(COMPARISON_KEY, JSON.stringify(list));
}

// Add property to comparison
function addToComparison(propertyId, propertyTitle, propertyPrice, propertyImage, propertyLocation) {
    let comparisonList = getComparisonList();
    
    // Check if already in comparison
    const exists = comparisonList.some(p => p.id === propertyId);
    if (exists) {
        showToast('Property already in comparison list', 'warning');
        return;
    }
    
    // Check maximum limit
    if (comparisonList.length >= MAX_COMPARISON) {
        showToast(`You can only compare up to ${MAX_COMPARISON} properties at once`, 'warning');
        return;
    }
    
    // Add property
    const property = {
        id: propertyId,
        title: propertyTitle,
        price: propertyPrice,
        image: propertyImage,
        location: propertyLocation,
        addedAt: new Date().toISOString()
    };
    
    comparisonList.push(property);
    saveComparisonList(comparisonList);
    
    updateComparisonBadge();
    updateComparisonButtons();
    showToast('Property added to comparison', 'success');
}

// Remove property from comparison
function removeFromComparison(propertyId) {
    let comparisonList = getComparisonList();
    comparisonList = comparisonList.filter(p => p.id !== propertyId);
    saveComparisonList(comparisonList);
    
    updateComparisonBadge();
    updateComparisonButtons();
    showToast('Property removed from comparison', 'info');
    
    // If we're on the comparison page, refresh it
    if (window.location.pathname.includes('/compare')) {
        loadComparisonPage();
    }
}

// Check if property is in comparison
function isInComparison(propertyId) {
    const comparisonList = getComparisonList();
    return comparisonList.some(p => p.id === propertyId);
}

// Update comparison badge count
function updateComparisonBadge() {
    const comparisonList = getComparisonList();
    const badges = document.querySelectorAll('.comparison-badge');
    
    badges.forEach(badge => {
        if (comparisonList.length > 0) {
            badge.textContent = comparisonList.length;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    });
}

// Update comparison button states
function updateComparisonButtons() {
    const buttons = document.querySelectorAll('[data-property-id]');
    
    buttons.forEach(button => {
        const propertyId = button.dataset.propertyId;
        if (propertyId && isInComparison(parseInt(propertyId))) {
            button.classList.add('btn-warning');
            button.classList.remove('btn-outline-secondary');
            button.innerHTML = '<i class="fas fa-check me-1"></i>In Comparison';
        }
    });
}

// Clear all comparisons
function clearAllComparisons() {
    if (confirm('Are you sure you want to clear all property comparisons?')) {
        localStorage.removeItem(COMPARISON_KEY);
        updateComparisonBadge();
        updateComparisonButtons();
        showToast('Comparison list cleared', 'info');
        
        if (window.location.pathname.includes('/compare')) {
            window.location.href = '/properties/';
        }
    }
}

// Show comparison sidebar
function showComparisonSidebar() {
    const comparisonList = getComparisonList();
    
    if (comparisonList.length === 0) {
        showToast('No properties in comparison list', 'info');
        return;
    }
    
    // Create sidebar HTML
    const sidebarHTML = `
        <div class="comparison-sidebar" id="comparisonSidebar">
            <div class="comparison-header">
                <h5><i class="fas fa-balance-scale me-2"></i>Compare Properties</h5>
                <button onclick="closeComparisonSidebar()" class="btn-close"></button>
            </div>
            <div class="comparison-body">
                ${comparisonList.map(property => `
                    <div class="comparison-item">
                        <img src="${property.image}" alt="${property.title}">
                        <div class="comparison-item-details">
                            <h6>${property.title}</h6>
                            <p class="small text-muted">${property.location}</p>
                            <p class="text-primary fw-bold">KSh ${parseInt(property.price).toLocaleString()}</p>
                        </div>
                        <button class="btn btn-sm btn-danger" onclick="removeFromComparison(${property.id})">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                `).join('')}
            </div>
            <div class="comparison-footer">
                <button class="btn btn-primary w-100 mb-2" onclick="viewComparison()">
                    <i class="fas fa-eye me-2"></i>Compare Now
                </button>
                <button class="btn btn-outline-danger w-100" onclick="clearAllComparisons()">
                    <i class="fas fa-trash me-2"></i>Clear All
                </button>
            </div>
        </div>
        <div class="comparison-overlay" id="comparisonOverlay" onclick="closeComparisonSidebar()"></div>
    `;
    
    // Remove existing sidebar
    const existing = document.getElementById('comparisonSidebar');
    if (existing) existing.remove();
    
    // Add to body
    document.body.insertAdjacentHTML('beforeend', sidebarHTML);
}

// Close comparison sidebar
function closeComparisonSidebar() {
    const sidebar = document.getElementById('comparisonSidebar');
    const overlay = document.getElementById('comparisonOverlay');
    
    if (sidebar) sidebar.remove();
    if (overlay) overlay.remove();
}

// View comparison page
function viewComparison() {
    const comparisonList = getComparisonList();
    const ids = comparisonList.map(p => p.id).join(',');
    window.location.href = `/properties/compare/?ids=${ids}`;
}

// Show toast notification
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 9999;';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show`;
    toast.style.cssText = 'min-width: 250px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 10px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Export functions to global scope
window.addToComparison = addToComparison;
window.removeFromComparison = removeFromComparison;
window.isInComparison = isInComparison;
window.showComparisonSidebar = showComparisonSidebar;
window.closeComparisonSidebar = closeComparisonSidebar;
window.viewComparison = viewComparison;
window.clearAllComparisons = clearAllComparisons;

