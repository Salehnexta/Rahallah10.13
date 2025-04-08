// Rahallah Trip Planner main JavaScript file

// Initialize Alpine.js components and interactions
document.addEventListener('alpine:init', () => {
    // Trip planner component
    Alpine.data('tripPlanner', () => ({
        scrollToBottom() {
            this.$el.scrollTop = this.$el.scrollHeight;
        },
        init() {
            this.scrollToBottom();
            
            // Listen for new messages and scroll to bottom
            this.$watch('$el.innerHTML', () => {
                this.scrollToBottom();
            });
        }
    }));
});

// Initialize any maps when the page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeMaps();
    
    // HTMX event listeners
    setupHtmxEventListeners();
});

// Initialize Leaflet maps if they exist on the page
function initializeMaps() {
    const mapContainers = document.querySelectorAll('.map-container');
    
    if (mapContainers.length === 0) return;
    
    mapContainers.forEach(container => {
        const mapId = container.id;
        const lat = parseFloat(container.dataset.lat || 25.2048);
        const lng = parseFloat(container.dataset.lng || 55.2708);
        const zoom = parseInt(container.dataset.zoom || 13);
        
        if (mapId) {
            const map = L.map(mapId).setView([lat, lng], zoom);
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(map);
            
            // Add marker if coordinates are provided
            if (container.dataset.lat && container.dataset.lng) {
                L.marker([lat, lng]).addTo(map);
            }
            
            // Store map instance for later use
            window[mapId + 'Map'] = map;
        }
    });
}

// Set up HTMX event listeners
function setupHtmxEventListeners() {
    // Handle after swap events to re-initialize dynamic content
    document.body.addEventListener('htmx:afterSwap', function(event) {
        // Re-initialize maps after content is loaded
        initializeMaps();
        
        // Scroll chat messages to bottom when new messages arrive
        const chatContainer = document.getElementById('chat-messages');
        if (chatContainer && event.target.id === 'chat-messages') {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    });
    
    // Handle modal close actions
    document.body.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal-backdrop') || 
            event.target.classList.contains('close-modal')) {
            const modal = document.querySelector('.modal-backdrop');
            if (modal) {
                modal.remove();
            }
        }
    });
    
    // Handle trip item changes
    document.body.addEventListener('htmx:afterRequest', function(event) {
        if (event.detail.path.includes('/api/add-to-trip') || 
            event.detail.path.includes('/api/remove-from-trip')) {
            // Send an event to trigger trip items refresh
            document.body.dispatchEvent(new Event('tripItemChange'));
        }
    });
    
    // When a form is submitted, show the loading indicator
    document.body.addEventListener('htmx:beforeRequest', function(event) {
        const form = event.target.closest('form');
        if (form) {
            const loadingIndicator = form.querySelector('.htmx-indicator');
            if (loadingIndicator) {
                loadingIndicator.style.display = 'flex';
            }
        }
    });
    
    // Hide the loading indicator after request completes
    document.body.addEventListener('htmx:afterRequest', function(event) {
        const form = event.target.closest('form');
        if (form) {
            const loadingIndicator = form.querySelector('.htmx-indicator');
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
        }
    });
}

// Format dates for display
function formatDate(dateString) {
    if (!dateString) return '';
    
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, options);
}
