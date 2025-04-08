// Global State Management
import { errorHandler, ERROR_TYPES, ERROR_CATEGORIES, ERROR_LEVELS } from './error-handler.js';

export const State = {
    init() {
        return {
            // Chat state
            messages: [],
            message: '',
            loading: false,
            error: null,
            session_id: null,

            // Trip state
            trip: {
                destination: null,
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
                }
            },

            // UI state
            showSidebar: false,
            showTripDetails: false,
            selectedTrip: null,

            // Error handling
            errors: [],
            errorCount: 0,
            lastError: null,

            // Event handlers
            init() {
                // Initialize session
                this.session_id = 'session_' + Math.random().toString(36).substr(2, 9);
                
                // Initialize WebSocket
                this.initWebSocket();
                
                // Register error handler
                errorHandler.registerCallback(ERROR_CATEGORIES.CHAT, (error) => {
                    this.handleError(error);
                });
                errorHandler.registerCallback(ERROR_CATEGORIES.TRIP_PLANNER, (error) => {
                    this.handleError(error);
                });
            },

            // WebSocket initialization
            initWebSocket() {
                try {
                    this.socket = io('/', {
                        transports: ['websocket'],
                        query: {
                            'X-Session-ID': this.session_id
                        }
                    });

                    // Event handlers
                    this.socket.on('connect', () => {
                        console.log('Connected to WebSocket server');
                    });

                    this.socket.on('disconnect', () => {
                        console.log('Disconnected from WebSocket server');
                        this.handleError({
                            type: ERROR_TYPES.NETWORK,
                            category: ERROR_CATEGORIES.CHAT,
                            level: ERROR_LEVELS.WARNING,
                            message: 'WebSocket connection lost'
                        });
                    });

                    this.socket.on('error', (error) => {
                        this.handleError({
                            type: ERROR_TYPES.NETWORK,
                            category: ERROR_CATEGORIES.CHAT,
                            level: ERROR_LEVELS.ERROR,
                            message: 'WebSocket error',
                            error
                        });
                    });

                    this.socket.on('initial_state', (state) => {
                        try {
                            this.messages = state.session?.conversation_history || [];
                            this.trip = state.cache?.trip || this.trip;
                            this.scrollToBottom();
                            this.handleError(null); // Clear any previous errors
                        } catch (error) {
                            this.handleError({
                                type: ERROR_TYPES.SERVER,
                                category: ERROR_CATEGORIES.CHAT,
                                level: ERROR_LEVELS.ERROR,
                                message: 'Failed to load initial state',
                                error
                            });
                        }
                    });

                    this.socket.on('response', (data) => {
                        try {
                            this.messages.push({
                                role: 'assistant',
                                content: data.message,
                                timestamp: new Date().toISOString()
                            });
                            this.trip = data.trip || this.trip;
                            this.scrollToBottom();
                            this.handleError(null); // Clear any previous errors
                        } catch (error) {
                            this.handleError({
                                type: ERROR_TYPES.SERVER,
                                category: ERROR_CATEGORIES.CHAT,
                                level: ERROR_LEVELS.ERROR,
                                message: 'Failed to process response',
                                error
                            });
                        }
                    });

                    this.socket.on('session_reset', () => {
                        try {
                            this.messages = [];
                            this.trip = {
                                destination: null,
                                dates: { start: null, end: null },
                                budget: { min: 0, max: 10000 },
                                preferences: {
                                    accommodation: [],
                                    activities: [],
                                    transportation: []
                                }
                            };
                            this.handleError(null); // Clear any previous errors
                        } catch (error) {
                            this.handleError({
                                type: ERROR_TYPES.SERVER,
                                category: ERROR_CATEGORIES.CHAT,
                                level: ERROR_LEVELS.ERROR,
                                message: 'Failed to reset session',
                                error
                            });
                        }
                    });
                } catch (error) {
                    this.handleError({
                        type: ERROR_TYPES.SYSTEM,
                        category: ERROR_CATEGORIES.CHAT,
                        level: ERROR_LEVELS.CRITICAL,
                        message: 'Failed to initialize WebSocket',
                        error
                    });
                }
            },

            // Error handling
            handleError(error) {
                if (!error) {
                    this.error = null;
                    this.errors = [];
                    this.errorCount = 0;
                    this.lastError = null;
                    return;
                }

                try {
                    // Validate error
                    errorHandler.validateError(error);

                    // Format error details
                    const errorDetails = errorHandler.getErrorDetails(error);

                    // Update state
                    this.error = errorDetails;
                    this.errors.push(errorDetails);
                    this.errorCount++;
                    this.lastError = errorDetails;

                    // Dispatch error event
                    this.$dispatch('error', errorDetails);

                    // Log error
                    errorHandler.logError(error);

                    // Show notification
                    this.$dispatch('notify', {
                        message: errorDetails.userMessage,
                        type: errorDetails.level
                    });

                    // Handle specific error types
                    switch (error.type) {
                        case ERROR_TYPES.NETWORK:
                            this.handleNetworkError(error);
                            break;
                        case ERROR_TYPES.VALIDATION:
                            this.handleValidationError(error);
                            break;
                        case ERROR_TYPES.SERVER:
                            this.handleServerError(error);
                            break;
                        case ERROR_TYPES.AUTH:
                            this.handleAuthError(error);
                            break;
                        case ERROR_TYPES.SYSTEM:
                            this.handleSystemError(error);
                            break;
                    }
                } catch (validationError) {
                    console.error('Error handling failed:', validationError);
                    this.handleError({
                        type: ERROR_TYPES.SYSTEM,
                        category: ERROR_CATEGORIES.SYSTEM,
                        level: ERROR_LEVELS.CRITICAL,
                        message: 'Error handling system failed',
                        error: validationError
                    });
                }
            },

            // Specific error handlers
            handleNetworkError(error) {
                // Implement network error specific handling
                this.$dispatch('notify', {
                    message: 'Network connection lost. Please check your internet connection.',
                    type: 'error'
                });
            },

            handleValidationError(error) {
                // Implement validation error specific handling
                this.$dispatch('notify', {
                    message: error.validationMessage || 'Invalid input. Please check your inputs.',
                    type: 'warning'
                });
            },

            handleServerError(error) {
                // Implement server error specific handling
                this.$dispatch('notify', {
                    message: 'Server error occurred. Please try again later.',
                    type: 'error'
                });
            },

            handleAuthError(error) {
                // Implement auth error specific handling
                this.$dispatch('notify', {
                    message: 'Authentication error. Please log in again.',
                    type: 'warning'
                });
            },

            handleSystemError(error) {
                // Implement system error specific handling
                this.$dispatch('notify', {
                    message: 'System error occurred. Please refresh the page.',
                    type: 'error'
                });
            },

            // Helper methods
            scrollToBottom() {
                try {
                    const messages = this.$refs.messages;
                    if (messages) {
                        messages.scrollTop = messages.scrollHeight;
                    }
                } catch (error) {
                    this.handleError({
                        type: ERROR_TYPES.SYSTEM,
                        category: ERROR_CATEGORIES.UI,
                        level: ERROR_LEVELS.ERROR,
                        message: 'Failed to scroll messages',
                        error
                    });
                }
            },

            // Chat methods
            sendMessage() {
                if (!this.message.trim()) {
                    this.handleError({
                        type: ERROR_TYPES.VALIDATION,
                        category: ERROR_CATEGORIES.CHAT,
                        level: ERROR_LEVELS.WARNING,
                        message: 'Message cannot be empty',
                        validationMessage: 'Please enter a message'
                    });
                    return;
                }

                try {
                    // Add user message to conversation
                    this.messages.push({
                        role: 'user',
                        content: this.message,
                        timestamp: new Date().toISOString()
                    });

                    // Emit message to server
                    this.socket.emit('message', { message: this.message });

                    // Clear input
                    this.message = '';
                    this.scrollToBottom();
                } catch (error) {
                    this.handleError({
                        type: ERROR_TYPES.SYSTEM,
                        category: ERROR_CATEGORIES.CHAT,
                        level: ERROR_LEVELS.ERROR,
                        message: 'Failed to send message',
                        error
                    });
                }
            },

            // Trip methods
            async searchTrips() {
                if (!this.validateTripForm()) return;

                try {
                    this.loading = true;
                    const response = await fetch('/api/search-trips', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(this.trip)
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const data = await response.json();
                    if (response.ok) {
                        this.socket.emit('search_results', data);
                    } else {
                        throw new Error(data.error || 'Failed to search trips');
                    }
                } catch (error) {
                    this.handleError({
                        type: ERROR_TYPES.SERVER,
                        category: ERROR_CATEGORIES.TRIP_PLANNER,
                        level: ERROR_LEVELS.ERROR,
                        message: 'Failed to search trips',
                        error
                    });
                } finally {
                    this.loading = false;
                }
            },

            validateTripForm() {
                const errors = [];

                if (!this.trip.destination) {
                    errors.push('Please select a destination');
                }

                if (!this.trip.dates.start || !this.trip.dates.end) {
                    errors.push('Please select both start and end dates');
                }

                if (this.trip.budget.min > this.trip.budget.max) {
                    errors.push('Minimum budget cannot be greater than maximum budget');
                }

                if (errors.length > 0) {
                    this.handleError({
                        type: ERROR_TYPES.VALIDATION,
                        category: ERROR_CATEGORIES.TRIP_PLANNER,
                        level: ERROR_LEVELS.WARNING,
                        message: 'Form validation failed',
                        validationMessage: errors.join('\n')
                    });
                    return false;
                }

                return true;
            },

            // UI methods
            toggleSidebar() {
                try {
                    this.showSidebar = !this.showSidebar;
                } catch (error) {
                    this.handleError({
                        type: ERROR_TYPES.SYSTEM,
                        category: ERROR_CATEGORIES.UI,
                        level: ERROR_LEVELS.ERROR,
                        message: 'Failed to toggle sidebar',
                        error
                    });
                }
            },

            selectTrip(tripId) {
                try {
                    this.selectedTrip = tripId;
                    this.showTripDetails = true;
                } catch (error) {
                    this.handleError({
                        type: ERROR_TYPES.SYSTEM,
                        category: ERROR_CATEGORIES.UI,
                        level: ERROR_LEVELS.ERROR,
                        message: 'Failed to select trip',
                        error
                    });
                }
            },

            resetTrip() {
                try {
                    this.trip = {
                        destination: null,
                        dates: { start: null, end: null },
                        budget: { min: 0, max: 10000 },
                        preferences: {
                            accommodation: [],
                            activities: [],
                            transportation: []
                        }
                    };
                    this.error = null;
                    this.errors = [];
                } catch (error) {
                    this.handleError({
                        type: ERROR_TYPES.SYSTEM,
                        category: ERROR_CATEGORIES.UI,
                        level: ERROR_LEVELS.ERROR,
                        message: 'Failed to reset trip',
                        error
                    });
                }
            }
        };
    }
};
