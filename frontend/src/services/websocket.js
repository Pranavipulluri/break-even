import { io } from 'socket.io-client';
import toast from 'react-hot-toast';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect(userId) {
    if (this.socket && this.isConnected) {
      return;
    }

    const serverUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
    
    this.socket = io(serverUrl, {
      auth: {
        token: localStorage.getItem('token')
      },
      transports: ['websocket', 'polling']
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.isConnected = true;
      this.reconnectAttempts = 0;
      
      // Join user's room for personalized notifications
      if (userId) {
        this.socket.emit('join_room', userId);
      }
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      this.isConnected = false;
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.handleReconnect();
    });

    // Handle new messages
    this.socket.on('new_message', (message) => {
      toast.success(`New message from ${message.customer_name}`);
      
      // Dispatch custom event for components to listen to
      window.dispatchEvent(new CustomEvent('newMessage', { detail: message }));
    });

    // Handle new customer registrations
    this.socket.on('new_customer', (customer) => {
      toast.success(`New customer registered: ${customer.name}`);
      
      window.dispatchEvent(new CustomEvent('newCustomer', { detail: customer }));
    });

    // Handle QR code scans
    this.socket.on('qr_scan', (data) => {
      toast.success('Your QR code was scanned!');
      
      window.dispatchEvent(new CustomEvent('qrScan', { detail: data }));
    });

    // Handle feedback submissions
    this.socket.on('new_feedback', (feedback) => {
      toast.success(`New feedback received (${feedback.rating} stars)`);
      
      window.dispatchEvent(new CustomEvent('newFeedback', { detail: feedback }));
    });
  }

  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        if (this.socket) {
          this.socket.connect();
        }
      }, 1000 * this.reconnectAttempts); // Exponential backoff
    } else {
      console.error('Max reconnection attempts reached');
      toast.error('Connection lost. Please refresh the page.');
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  // Method to emit events
  emit(event, data) {
    if (this.socket && this.isConnected) {
      this.socket.emit(event, data);
    }
  }

  // Method to listen to custom events
  on(event, callback) {
    if (this.socket) {
      this.socket.on(event, callback);
    }
  }

  // Method to remove event listeners
  off(event, callback) {
    if (this.socket) {
      this.socket.off(event, callback);
    }
  }
}

// Create a singleton instance
const webSocketService = new WebSocketService();

export default webSocketService;
