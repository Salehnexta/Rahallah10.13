// WebSocket utilities
export const WebSocketUtils = {
    initWebSocket(sessionId) {
        // Initialize Socket.IO client
        const socket = io('/', {
            transports: ['websocket'],
            query: {
                'X-Session-ID': sessionId
            }
        });

        // Handle connection
        socket.on('connect', () => {
            console.log('Connected to WebSocket server');
        });

        // Handle disconnection
        socket.on('disconnect', () => {
            console.log('Disconnected from WebSocket server');
        });

        // Handle errors
        socket.on('error', (error) => {
            console.error('WebSocket error:', error);
        });

        return socket;
    }
};
