import { useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import webSocketService from '../services/websocket';

export const useWebSocket = () => {
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      // Connect to WebSocket when user is authenticated
      webSocketService.connect(user.id);
    }

    return () => {
      // Disconnect when component unmounts or user changes
      if (!user) {
        webSocketService.disconnect();
      }
    };
  }, [user]);

  return {
    socket: webSocketService.socket,
    isConnected: webSocketService.isConnected,
    emit: webSocketService.emit.bind(webSocketService),
    on: webSocketService.on.bind(webSocketService),
    off: webSocketService.off.bind(webSocketService)
  };
};