/**
 * Social Sharing Functions
 * Traca Management Services
 */

// Share on WhatsApp
function shareOnWhatsApp(url, text) {
    const message = encodeURIComponent(`${text}\n\n${url}`);
    const whatsappUrl = `https://wa.me/?text=${message}`;
    window.open(whatsappUrl, '_blank');
}

// Share on Facebook
function shareOnFacebook(url) {
    const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
    window.open(facebookUrl, '_blank', 'width=600,height=400');
}

// Share on Twitter
function shareOnTwitter(url, text) {
    const twitterUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`;
    window.open(twitterUrl, '_blank', 'width=600,height=400');
}

// Share on LinkedIn
function shareOnLinkedIn(url) {
    const linkedinUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;
    window.open(linkedinUrl, '_blank', 'width=600,height=400');
}

// Share via Email
function shareViaEmail(subject, body) {
    const mailtoUrl = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    window.location.href = mailtoUrl;
}

// Copy link to clipboard
function copyLinkToClipboard(url, buttonElement) {
    navigator.clipboard.writeText(url).then(function() {
        // Show success feedback
        const originalHTML = buttonElement.innerHTML;
        buttonElement.innerHTML = '<i class="fas fa-check me-2"></i>Link Copied!';
        buttonElement.classList.add('copied');
        
        // Revert after 2 seconds
        setTimeout(function() {
            buttonElement.innerHTML = originalHTML;
            buttonElement.classList.remove('copied');
        }, 2000);
        
        // Show toast notification
        showShareToast('Link copied to clipboard!', 'success');
    }).catch(function(err) {
        console.error('Failed to copy link:', err);
        showShareToast('Failed to copy link', 'danger');
    });
}

// Share property
function shareProperty(propertyTitle, propertyPrice, propertyLocation) {
    const url = window.location.href;
    const text = `Check out this property: ${propertyTitle} - KSh ${propertyPrice} in ${propertyLocation}`;
    
    // Check if native share API is available (mobile)
    if (navigator.share) {
        navigator.share({
            title: propertyTitle,
            text: text,
            url: url
        }).catch(err => console.log('Error sharing:', err));
    } else {
        // Fallback to custom share modal
        showShareModal(propertyTitle, url, text);
    }
}

// Show share modal
function showShareModal(title, url, text) {
    const modalHTML = `
        <div class="modal fade" id="shareModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-share-alt me-2"></i>Share this Property
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p class="text-muted">${title}</p>
                        <div class="social-share-buttons">
                            <button class="social-share-btn whatsapp" onclick="shareOnWhatsApp('${url}', '${text}')">
                                <i class="fab fa-whatsapp"></i> WhatsApp
                            </button>
                            <button class="social-share-btn facebook" onclick="shareOnFacebook('${url}')">
                                <i class="fab fa-facebook"></i> Facebook
                            </button>
                            <button class="social-share-btn twitter" onclick="shareOnTwitter('${url}', '${text}')">
                                <i class="fab fa-twitter"></i> Twitter
                            </button>
                            <button class="social-share-btn linkedin" onclick="shareOnLinkedIn('${url}')">
                                <i class="fab fa-linkedin"></i> LinkedIn
                            </button>
                            <button class="social-share-btn email" onclick="shareViaEmail('${encodeURIComponent(title)}', '${encodeURIComponent(text + '\\n\\n' + url)}')">
                                <i class="fas fa-envelope"></i> Email
                            </button>
                            <button class="social-share-btn copy-link" onclick="copyLinkToClipboard('${url}', this)">
                                <i class="fas fa-link me-2"></i>Copy Link
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal
    const existing = document.getElementById('shareModal');
    if (existing) existing.remove();
    
    // Add to body
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('shareModal'));
    modal.show();
}

// Show toast notification for sharing
function showShareToast(message, type = 'info') {
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 9999;';
        document.body.appendChild(toastContainer);
    }
    
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show`;
    toast.style.cssText = 'min-width: 250px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 10px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Export functions to global scope
window.shareOnWhatsApp = shareOnWhatsApp;
window.shareOnFacebook = shareOnFacebook;
window.shareOnTwitter = shareOnTwitter;
window.shareOnLinkedIn = shareOnLinkedIn;
window.shareViaEmail = shareViaEmail;
window.copyLinkToClipboard = copyLinkToClipboard;
window.shareProperty = shareProperty;
window.showShareModal = showShareModal;

