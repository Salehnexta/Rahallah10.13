// Error types
export const ERROR_TYPES = {
    NETWORK: 'network',
    VALIDATION: 'validation',
    SERVER: 'server',
    AUTH: 'auth',
    SYSTEM: 'system',
    UNKNOWN: 'unknown'
};

// Error categories
export const ERROR_CATEGORIES = {
    TRIP_PLANNER: 'trip_planner',
    CHAT: 'chat',
    AUTHENTICATION: 'authentication',
    API: 'api',
    UI: 'ui'
};

// Error levels
export const ERROR_LEVELS = {
    INFO: 'info',
    WARNING: 'warning',
    ERROR: 'error',
    CRITICAL: 'critical'
};

// Error handler class
export class ErrorHandler {
    constructor() {
        this.errorLog = [];
        this.errorCallbacks = new Map();
        
        // Initialize error handling
        this.setupGlobalHandlers();
    }

    // Setup global error handlers
    setupGlobalHandlers() {
        // Global unhandled promise rejection handler
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError({
                type: ERROR_TYPES.SYSTEM,
                category: ERROR_CATEGORIES.SYSTEM,
                level: ERROR_LEVELS.CRITICAL,
                message: 'Unhandled promise rejection',
                error: event.reason
            });
        });

        // Global error handler
        window.addEventListener('error', (event) => {
            this.handleError({
                type: ERROR_TYPES.SYSTEM,
                category: ERROR_CATEGORIES.SYSTEM,
                level: ERROR_LEVELS.CRITICAL,
                message: 'Global error occurred',
                error: event.error
            });
        });
    }

    // Register error callback
    registerCallback(category, callback) {
        if (!this.errorCallbacks.has(category)) {
            this.errorCallbacks.set(category, []);
        }
        this.errorCallbacks.get(category).push(callback);
    }

    // Unregister error callback
    unregisterCallback(category, callback) {
        if (this.errorCallbacks.has(category)) {
            const callbacks = this.errorCallbacks.get(category);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }

    // Handle error
    handleError(error) {
        // Log error
        this.logError(error);

        // Notify callbacks
        this.notifyCallbacks(error);

        // Dispatch global error event
        this.dispatchGlobalError(error);

        // Return error object for chaining
        return error;
    }

    // Log error
    logError(error) {
        const timestamp = new Date().toISOString();
        const logEntry = {
            ...error,
            timestamp,
            userAgent: navigator.userAgent
        };

        // Add to local error log
        this.errorLog.push(logEntry);

        // Send to server if configured
        if (window.errorReportingEnabled) {
            this.sendErrorToServer(logEntry);
        }

        // Store in localStorage for debugging
        const storedErrors = JSON.parse(localStorage.getItem('errorLog') || '[]');
        storedErrors.push(logEntry);
        localStorage.setItem('errorLog', JSON.stringify(storedErrors));
    }

    // Send error to server
    async sendErrorToServer(error) {
        try {
            await fetch('/api/error-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(error)
            });
        } catch (err) {
            console.error('Failed to send error report:', err);
        }
    }

    // Notify registered callbacks
    notifyCallbacks(error) {
        if (this.errorCallbacks.has(error.category)) {
            const callbacks = this.errorCallbacks.get(error.category);
            callbacks.forEach(callback => callback(error));
        }
    }

    // Dispatch global error event
    dispatchGlobalError(error) {
        window.dispatchEvent(new CustomEvent('error', {
            detail: error
        }));
    }

    // Get error details
    getErrorDetails(error) {
        const details = {
            message: error.message || 'An error occurred',
            type: error.type || ERROR_TYPES.UNKNOWN,
            level: error.level || ERROR_LEVELS.ERROR,
            timestamp: error.timestamp || new Date().toISOString(),
            stack: error.stack || null
        };

        // Add user-friendly message based on error type
        switch (error.type) {
            case ERROR_TYPES.NETWORK:
                details.userMessage = 'Network connection error. Please check your internet connection.';
                break;
            case ERROR_TYPES.VALIDATION:
                details.userMessage = error.validationMessage || 'Invalid input. Please check your inputs.';
                break;
            case ERROR_TYPES.SERVER:
                details.userMessage = 'Server error occurred. Please try again later.';
                break;
            case ERROR_TYPES.AUTH:
                details.userMessage = 'Authentication error. Please log in again.';
                break;
            case ERROR_TYPES.SYSTEM:
                details.userMessage = 'System error occurred. Please refresh the page.';
                break;
            default:
                details.userMessage = 'An unexpected error occurred. Please try again.';
        }

        return details;
    }

    // Clear error log
    clearErrorLog() {
        this.errorLog = [];
        localStorage.removeItem('errorLog');
    }

    // Get recent errors
    getRecentErrors(limit = 10) {
        return this.errorLog.slice(-limit);
    }

    // Create error object
    createError(error, category = ERROR_CATEGORIES.SYSTEM, level = ERROR_LEVELS.ERROR) {
        return {
            message: error.message || error,
            type: error.type || ERROR_TYPES.UNKNOWN,
            category,
            level,
            stack: error.stack,
            validationMessage: error.validationMessage,
            error: error instanceof Error ? error : null
        };
    }

    // Validate error object
    validateError(error) {
        if (!error || typeof error !== 'object') {
            throw new Error('Error object must be provided');
        }

        if (!error.message) {
            throw new Error('Error message is required');
        }

        if (!ERROR_TYPES[error.type]) {
            throw new Error(`Invalid error type: ${error.type}`);
        }

        if (!ERROR_CATEGORIES[error.category]) {
            throw new Error(`Invalid error category: ${error.category}`);
        }

        if (!ERROR_LEVELS[error.level]) {
            throw new Error(`Invalid error level: ${error.level}`);
        }
    }
}

// Export singleton instance
export const errorHandler = new ErrorHandler();
