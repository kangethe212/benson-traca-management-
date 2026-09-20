/**
 * TRACA Management - Performance Optimizations
 * Enhanced mobile responsiveness and performance for Android 8+ devices
 */

// Performance monitoring and optimization utilities
class TRACAPerformance {
    constructor() {
        this.init();
    }

    init() {
        this.setupPerformanceMonitoring();
        this.setupLazyLoading();
        this.setupImageOptimization();
        this.setupMobileOptimizations();
        this.setupCaching();
        this.setupIntersectionObserver();
    }

    // Performance monitoring
    setupPerformanceMonitoring() {
        // Monitor page load performance
        if ('performance' in window) {
            window.addEventListener('load', () => {
                const perfData = performance.getEntriesByType('navigation')[0];
                const loadTime = perfData.loadEventEnd - perfData.loadEventStart;
                
                // Log performance metrics
                console.log('Page Load Time:', loadTime + 'ms');
                
                // Send to analytics if available
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'page_load_time', {
                        'custom_parameter': loadTime
                    });
                }
            });
        }

        // Monitor Core Web Vitals
        this.setupWebVitals();
    }

    setupWebVitals() {
        // Largest Contentful Paint (LCP)
        if ('PerformanceObserver' in window) {
            const lcpObserver = new PerformanceObserver((entryList) => {
                const entries = entryList.getEntries();
                const lastEntry = entries[entries.length - 1];
                console.log('LCP:', lastEntry.startTime);
            });
            lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

            // First Input Delay (FID)
            const fidObserver = new PerformanceObserver((entryList) => {
                const entries = entryList.getEntries();
                entries.forEach(entry => {
                    console.log('FID:', entry.processingStart - entry.startTime);
                });
            });
            fidObserver.observe({ entryTypes: ['first-input'] });

            // Cumulative Layout Shift (CLS)
            let clsValue = 0;
            const clsObserver = new PerformanceObserver((entryList) => {
                for (const entry of entryList.getEntries()) {
                    if (!entry.hadRecentInput) {
                        clsValue += entry.value;
                    }
                }
                console.log('CLS:', clsValue);
            });
            clsObserver.observe({ entryTypes: ['layout-shift'] });
        }
    }

    // Enhanced lazy loading for images and content
    setupLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        
                        // Load image
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                            img.classList.remove('lazy');
                            img.classList.add('loaded');
                        }
                        
                        imageObserver.unobserve(img);
                    }
                });
            }, {
                rootMargin: '50px 0px',
                threshold: 0.01
            });

            // Observe all lazy images
            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });

            // Lazy load content sections
            const contentObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const element = entry.target;
                        
                        // Add animation classes
                        element.classList.add('fade-in-up');
                        contentObserver.unobserve(element);
                    }
                });
            }, {
                rootMargin: '25px 0px',
                threshold: 0.1
            });

            document.querySelectorAll('.property-card, .trust-item, .stat-item').forEach(el => {
                contentObserver.observe(el);
            });
        }
    }

    // Image optimization
    setupImageOptimization() {
        // Add loading="lazy" to all images that don't have it
        document.querySelectorAll('img:not([loading])').forEach(img => {
            img.setAttribute('loading', 'lazy');
        });

        // Optimize image sizes based on viewport
        this.optimizeImageSizes();
        
        // Setup responsive images
        this.setupResponsiveImages();
    }

    optimizeImageSizes() {
        const images = document.querySelectorAll('img');
        const viewportWidth = window.innerWidth;

        images.forEach(img => {
            const naturalWidth = img.naturalWidth;
            if (naturalWidth > viewportWidth * 2) {
                // Image is too large for viewport
                img.style.maxWidth = '100%';
                img.style.height = 'auto';
            }
        });
    }

    setupResponsiveImages() {
        // Create responsive image sources for different screen sizes
        const propertyImages = document.querySelectorAll('.property-image img');
        
        propertyImages.forEach(img => {
            const src = img.src;
            if (src.includes('/media/')) {
                // Create different sizes for different viewports
                const sizes = [
                    { width: 400, suffix: '_small' },
                    { width: 800, suffix: '_medium' },
                    { width: 1200, suffix: '_large' }
                ];

                let srcset = '';
                sizes.forEach(size => {
                    const sizedSrc = src.replace(/\.(jpg|jpeg|png|webp)$/, `${size.suffix}.$1`);
                    srcset += `${sizedSrc} ${size.width}w, `;
                });

                if (srcset) {
                    img.srcset = srcset.slice(0, -2);
                    img.sizes = '(max-width: 768px) 400px, (max-width: 1200px) 800px, 1200px';
                }
            }
        });
    }

    // Mobile-specific optimizations
    setupMobileOptimizations() {
        // Touch optimization
        this.setupTouchOptimization();
        
        // Viewport optimization
        this.setupViewportOptimization();
        
        // Mobile performance
        this.setupMobilePerformance();
    }

    setupTouchOptimization() {
        // Add touch-friendly interactions
        const touchElements = document.querySelectorAll('.btn, .property-card, .stat-item');
        
        touchElements.forEach(element => {
            element.addEventListener('touchstart', function() {
                this.classList.add('touch-active');
            });

            element.addEventListener('touchend', function() {
                setTimeout(() => {
                    this.classList.remove('touch-active');
                }, 150);
            });
        });

        // Prevent double-tap zoom on interactive elements
        let lastTouchEnd = 0;
        document.addEventListener('touchend', function(event) {
            const now = Date.now();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
    }

    setupViewportOptimization() {
        // Optimize viewport for mobile devices
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        
        if (isMobile) {
            // Set appropriate viewport meta tag
            const viewport = document.querySelector('meta[name="viewport"]');
            if (viewport) {
                viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes';
            }
        }
    }

    setupMobilePerformance() {
        // Reduce animations on mobile for better performance
        const isMobile = window.innerWidth <= 768;
        
        if (isMobile) {
            // Disable heavy animations on low-end devices
            const isLowEnd = navigator.hardwareConcurrency <= 2 || navigator.deviceMemory <= 2;
            
            if (isLowEnd) {
                document.body.classList.add('low-end-device');
                
                // Disable parallax and other heavy effects
                const parallaxElements = document.querySelectorAll('.hero-background');
                parallaxElements.forEach(el => {
                    el.style.backgroundAttachment = 'scroll';
                });
            }
        }
    }

    // Caching strategies
    setupCaching() {
        // Service Worker registration for caching
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/static/js/sw.js')
                    .then(registration => {
                        console.log('SW registered: ', registration);
                    })
                    .catch(registrationError => {
                        console.log('SW registration failed: ', registrationError);
                    });
            });
        }

        // Local storage for user preferences
        this.setupLocalStorage();
    }

    setupLocalStorage() {
        // Cache user preferences
        const preferences = {
            liked_properties: [],
            viewed_properties: [],
            search_history: [],
            filter_preferences: {}
        };

        // Initialize if not exists
        if (!localStorage.getItem('traca_preferences')) {
            localStorage.setItem('traca_preferences', JSON.stringify(preferences));
        }
    }

    // Intersection Observer for various elements
    setupIntersectionObserver() {
        // Animate elements on scroll
        const animateOnScroll = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, {
            threshold: 0.1
        });

        document.querySelectorAll('.hero-badge, .hero-main-title, .hero-subtitle, .hero-description').forEach(el => {
            animateOnScroll.observe(el);
        });
    }

    // Debounce utility for performance
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Throttle utility for scroll events
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// Enhanced search functionality
class EnhancedSearch {
    constructor() {
        this.searchInput = null;
        this.suggestionsContainer = null;
        this.debounceTimer = null;
        this.init();
    }

    init() {
        this.setupSearchElements();
        this.setupSearchListeners();
        this.setupAutocomplete();
    }

    setupSearchElements() {
        this.searchInput = document.querySelector('input[name="county"], .search-input');
        this.suggestionsContainer = document.getElementById('search-suggestions');
    }

    setupSearchListeners() {
        if (this.searchInput) {
            // Debounced search
            this.searchInput.addEventListener('input', (e) => {
                clearTimeout(this.debounceTimer);
                this.debounceTimer = setTimeout(() => {
                    this.handleSearch(e.target.value);
                }, 300);
            });

            // Keyboard navigation
            this.searchInput.addEventListener('keydown', (e) => {
                this.handleKeyboardNavigation(e);
            });

            // Close on escape
            this.searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.hideSuggestions();
                }
            });
        }
    }

    setupAutocomplete() {
        // County suggestions
        this.counties = [
            'Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret', 'Kisii', 'Thika',
            'Kitale', 'Garissa', 'Kakamega', 'Nyeri', 'Meru', 'Embu', 'Machakos',
            'Bungoma', 'Lodwar', 'Webuye', 'Kericho', 'Naivasha', 'Malindi'
        ];
    }

    async handleSearch(query) {
        if (query.length < 2) {
            this.hideSuggestions();
            return;
        }

        // Show loading state
        this.showLoadingState();

        try {
            // Try API first, fallback to local data
            let suggestions = [];
            
            try {
                const response = await fetch(`/api/search/?q=${encodeURIComponent(query)}`);
                if (!response.ok) {
                    throw new Error('search-api-' + response.status);
                }
                const data = await response.json();
                suggestions = data.suggestions || data.properties || [];
            } catch (apiError) {
                // Fallback to local county search
                suggestions = this.counties
                    .filter(county => county.toLowerCase().includes(query.toLowerCase()))
                    .map(county => ({
                        title: county,
                        type: 'county',
                        url: `/properties/?county=${encodeURIComponent(county)}`
                    }));
            }

            this.showSuggestions(suggestions);
        } catch (error) {
            console.error('Search error:', error);
            this.hideSuggestions();
        }
    }

    showSuggestions(suggestions) {
        if (!this.suggestionsContainer) {
            this.createSuggestionsContainer();
        }

        this.suggestionsContainer.innerHTML = '';

        if (suggestions.length === 0) {
            this.suggestionsContainer.innerHTML = '<div class="suggestion-item no-results">No results found</div>';
        } else {
            suggestions.forEach(suggestion => {
                const item = document.createElement('div');
                item.className = 'suggestion-item';
                item.innerHTML = `
                    <div class="suggestion-icon">
                        <i class="fas fa-${this.getIconForType(suggestion.type)}"></i>
                    </div>
                    <div class="suggestion-content">
                        <div class="suggestion-title">${suggestion.title}</div>
                        ${suggestion.county ? `<div class="suggestion-subtitle">${suggestion.county}</div>` : ''}
                        ${suggestion.price ? `<div class="suggestion-price">KSh ${suggestion.price.toLocaleString()}</div>` : ''}
                    </div>
                `;
                
                item.addEventListener('click', () => {
                    window.location.href = suggestion.url;
                });

                this.suggestionsContainer.appendChild(item);
            });
        }

        this.suggestionsContainer.style.display = 'block';
    }

    createSuggestionsContainer() {
        this.suggestionsContainer = document.createElement('div');
        this.suggestionsContainer.id = 'search-suggestions';
        this.suggestionsContainer.className = 'search-suggestions';
        this.suggestionsContainer.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #e0e0e0;
            border-top: none;
            max-height: 300px;
            overflow-y: auto;
            z-index: 1000;
            border-radius: 0 0 10px 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        `;

        const searchForm = this.searchInput.closest('form');
        if (searchForm) {
            searchForm.style.position = 'relative';
            searchForm.appendChild(this.suggestionsContainer);
        }
    }

    showLoadingState() {
        if (!this.suggestionsContainer) {
            this.createSuggestionsContainer();
        }

        this.suggestionsContainer.innerHTML = `
            <div class="suggestion-item loading">
                <div class="loading-spinner"></div>
                <span>Searching...</span>
            </div>
        `;
        this.suggestionsContainer.style.display = 'block';
    }

    hideSuggestions() {
        if (this.suggestionsContainer) {
            this.suggestionsContainer.style.display = 'none';
        }
    }

    handleKeyboardNavigation(e) {
        const items = this.suggestionsContainer?.querySelectorAll('.suggestion-item') || [];
        let currentIndex = -1;

        // Find current selected item
        items.forEach((item, index) => {
            if (item.classList.contains('selected')) {
                currentIndex = index;
            }
        });

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                currentIndex = Math.min(currentIndex + 1, items.length - 1);
                this.selectSuggestionItem(items, currentIndex);
                break;
            case 'ArrowUp':
                e.preventDefault();
                currentIndex = Math.max(currentIndex - 1, 0);
                this.selectSuggestionItem(items, currentIndex);
                break;
            case 'Enter':
                e.preventDefault();
                if (currentIndex >= 0 && items[currentIndex]) {
                    items[currentIndex].click();
                }
                break;
        }
    }

    selectSuggestionItem(items, index) {
        items.forEach(item => item.classList.remove('selected'));
        if (items[index]) {
            items[index].classList.add('selected');
            items[index].scrollIntoView({ block: 'nearest' });
        }
    }

    getIconForType(type) {
        const icons = {
            'property': 'home',
            'county': 'map-marker-alt',
            'town': 'city'
        };
        return icons[type] || 'search';
    }
}

// Filter management
class FilterManager {
    constructor() {
        this.filters = new Map();
        this.init();
    }

    init() {
        this.setupFilterTabs();
        this.setupFilterPersistence();
        this.setupFilterReset();
    }

    setupFilterTabs() {
        const tabs = document.querySelectorAll('.filter-tab');
        const panels = document.querySelectorAll('.filter-panel');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetPanel = tab.dataset.tab;

                // Update active states
                tabs.forEach(t => t.classList.remove('active'));
                panels.forEach(p => p.classList.remove('active'));

                tab.classList.add('active');
                document.querySelector(`[data-panel="${targetPanel}"]`).classList.add('active');

                // Save active tab
                localStorage.setItem('active_filter_tab', targetPanel);
            });
        });

        // Restore active tab
        const activeTab = localStorage.getItem('active_filter_tab');
        if (activeTab) {
            const tab = document.querySelector(`[data-tab="${activeTab}"]`);
            if (tab) tab.click();
        }
    }

    setupFilterPersistence() {
        // Save filter values to localStorage
        const filterInputs = document.querySelectorAll('.filter-input');
        
        filterInputs.forEach(input => {
            // Restore saved value
            const savedValue = localStorage.getItem(`filter_${input.name}`);
            if (savedValue) {
                input.value = savedValue;
            }

            // Save on change
            input.addEventListener('change', () => {
                localStorage.setItem(`filter_${input.name}`, input.value);
            });
        });
    }

    setupFilterReset() {
        const resetButton = document.querySelector('.btn-reset');
        if (resetButton) {
            resetButton.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Clear localStorage
                Object.keys(localStorage).forEach(key => {
                    if (key.startsWith('filter_')) {
                        localStorage.removeItem(key);
                    }
                });

                // Clear form
                const form = document.querySelector('.filter-form');
                if (form) {
                    form.reset();
                }

                // Redirect to clean URL
                window.location.href = window.location.pathname;
            });
        }
    }
}

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize performance optimizations
    window.TRACA = new TRACAPerformance();
    
    // Initialize enhanced search
    window.enhancedSearch = new EnhancedSearch();
    
    // Initialize filter manager
    window.filterManager = new FilterManager();
    
    // Add global utility functions
    window.TRACAUtils = {
        // Format currency
        formatCurrency: (amount) => {
            return new Intl.NumberFormat('en-KE', {
                style: 'currency',
                currency: 'KES',
                minimumFractionDigits: 0
            }).format(amount);
        },

        // Format date
        formatDate: (date) => {
            return new Intl.DateTimeFormat('en-KE', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            }).format(new Date(date));
        },

        // Debounce utility
        debounce: (func, wait) => {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        // Throttle utility
        throttle: (func, limit) => {
            let inThrottle;
            return function() {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        }
    };
});

// Add CSS for suggestions
const suggestionStyles = `
    .search-suggestions {
        display: none;
    }
    
    .suggestion-item {
        padding: 12px 16px;
        cursor: pointer;
        border-bottom: 1px solid #f0f0f0;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: background-color 0.2s;
    }
    
    .suggestion-item:hover,
    .suggestion-item.selected {
        background-color: #f8f9fa;
    }
    
    .suggestion-item.loading {
        justify-content: center;
        color: #666;
    }
    
    .suggestion-item.no-results {
        justify-content: center;
        color: #999;
        font-style: italic;
    }
    
    .suggestion-icon {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, var(--brand-magenta), var(--brand-bright-pink));
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 14px;
    }
    
    .suggestion-content {
        flex: 1;
    }
    
    .suggestion-title {
        font-weight: 600;
        color: #333;
        margin-bottom: 2px;
    }
    
    .suggestion-subtitle {
        font-size: 14px;
        color: #666;
    }
    
    .suggestion-price {
        font-size: 14px;
        color: var(--brand-magenta);
        font-weight: 600;
    }
    
    .loading-spinner {
        width: 16px;
        height: 16px;
        border: 2px solid #f3f3f3;
        border-top: 2px solid var(--brand-magenta);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-right: 8px;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .touch-active {
        opacity: 0.8;
        transform: scale(0.98);
    }
    
    .low-end-device * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
    
    .fade-in-up {
        opacity: 0;
        transform: translateY(20px);
        animation: fadeInUp 0.6s ease-out forwards;
    }
    
    @keyframes fadeInUp {
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;

// Inject styles
if (!document.querySelector('#traca-performance-styles')) {
    const styleSheet = document.createElement('style');
    styleSheet.id = 'traca-performance-styles';
    styleSheet.textContent = suggestionStyles;
    document.head.appendChild(styleSheet);
}
