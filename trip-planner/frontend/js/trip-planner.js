// Trip Planner Component
export const TripPlanner = {
    init() {
        // Initialize Alpine.js component
        return {
            destinations: [],
            selectedDestination: null,
            dates: {
                start: null,
                end: null
            },
            budget: {
                min: 0,
                max: 10000
            },
            preferences: {
                accommodation: [],
                activities: [],
                transportation: []
            },
            loading: false,
            error: null,

            init() {
                // Initialize date pickers
                this.initializeDatePickers();
                // Load destination suggestions
                this.loadDestinations();
            },

            initializeDatePickers() {
                // Add date picker functionality
                const startDateInput = document.getElementById('start-date');
                const endDateInput = document.getElementById('end-date');

                if (startDateInput && endDateInput) {
                    startDateInput.addEventListener('change', () => {
                        endDateInput.min = startDateInput.value;
                    });
                }
            },

            async loadDestinations() {
                try {
                    this.loading = true;
                    const response = await fetch('/api/destinations');
                    const data = await response.json();
                    this.destinations = data.destinations;
                } catch (error) {
                    this.error = 'Failed to load destinations';
                    console.error(error);
                } finally {
                    this.loading = false;
                }
            },

            async searchTrips() {
                if (!this.validateForm()) return;

                try {
                    this.loading = true;
                    const response = await fetch('/api/search-trips', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            destination: this.selectedDestination,
                            dates: this.dates,
                            budget: this.budget,
                            preferences: this.preferences
                        })
                    });

                    const data = await response.json();
                    if (response.ok) {
                        // Emit search results to chat
                        if (window.chatApp) {
                            window.chatApp.socket.emit('search_results', data);
                        }
                    } else {
                        this.error = data.error || 'Failed to search trips';
                    }
                } catch (error) {
                    this.error = 'Failed to search trips';
                    console.error(error);
                } finally {
                    this.loading = false;
                }
            },

            validateForm() {
                if (!this.selectedDestination) {
                    this.error = 'Please select a destination';
                    return false;
                }

                if (!this.dates.start || !this.dates.end) {
                    this.error = 'Please select both start and end dates';
                    return false;
                }

                return true;
            },

            resetForm() {
                this.selectedDestination = null;
                this.dates = { start: null, end: null };
                this.budget = { min: 0, max: 10000 };
                this.preferences = {
                    accommodation: [],
                    activities: [],
                    transportation: []
                };
                this.error = null;
            }
        };
    }
};
