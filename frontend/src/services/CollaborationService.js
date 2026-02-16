/**
 * CollaborationService.js
 * Real-time collaboration service for CrucibAI
 * Handles WebSocket connections, presence, live cursors, and shared editing
 */

class CollaborationService {
  constructor() {
    this.ws = null;
    this.projectId = null;
    this.userId = null;
    this.username = null;
    this.listeners = {};
    this.presenceMap = new Map(); // userId -> presence data
    this.cursorMap = new Map(); // userId -> cursor position
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
  }

  /**
   * Initialize collaboration service
   */
  init(projectId, userId, username) {
    this.projectId = projectId;
    this.userId = userId;
    this.username = username;
    this.connect();
  }

  /**
   * Connect to WebSocket
   */
  connect() {
    if (this.isConnected) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/projects/${this.projectId}`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('✅ WebSocket connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;

        // Send presence
        this.sendPresence();

        // Emit connected event
        this.emit('connected', { userId: this.userId, username: this.username });
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        this.emit('error', error);
      };

      this.ws.onclose = () => {
        console.log('WebSocket closed');
        this.isConnected = false;
        this.attemptReconnect();
      };
    } catch (e) {
      console.error('Failed to create WebSocket:', e);
      this.attemptReconnect();
    }
  }

  /**
   * Attempt to reconnect
   */
  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      setTimeout(() => this.connect(), this.reconnectDelay);
    } else {
      console.error('Max reconnect attempts reached');
      this.emit('disconnected', { reason: 'max_attempts' });
    }
  }

  /**
   * Send presence update
   */
  sendPresence() {
    if (!this.isConnected || !this.ws) return;

    const presence = {
      type: 'presence',
      userId: this.userId,
      username: this.username,
      timestamp: Date.now(),
      status: 'active',
    };

    this.ws.send(JSON.stringify(presence));
  }

  /**
   * Update cursor position
   */
  updateCursor(line, column, fileName) {
    if (!this.isConnected || !this.ws) return;

    const cursor = {
      type: 'cursor',
      userId: this.userId,
      username: this.username,
      line,
      column,
      fileName,
      timestamp: Date.now(),
    };

    this.ws.send(JSON.stringify(cursor));
  }

  /**
   * Send code edit
   */
  sendEdit(fileName, content, startLine, endLine) {
    if (!this.isConnected || !this.ws) return;

    const edit = {
      type: 'edit',
      userId: this.userId,
      fileName,
      content,
      startLine,
      endLine,
      timestamp: Date.now(),
    };

    this.ws.send(JSON.stringify(edit));
  }

  /**
   * Send agent progress update
   */
  sendAgentProgress(agentName, status, progress, phase) {
    if (!this.isConnected || !this.ws) return;

    const update = {
      type: 'agent_progress',
      agent: agentName,
      status,
      progress,
      phase,
      timestamp: Date.now(),
    };

    this.ws.send(JSON.stringify(update));
  }

  /**
   * Handle incoming WebSocket message
   */
  handleMessage(data) {
    const { type } = data;

    switch (type) {
      case 'presence':
        this.handlePresence(data);
        break;
      case 'cursor':
        this.handleCursor(data);
        break;
      case 'edit':
        this.handleEdit(data);
        break;
      case 'agent_progress':
        this.handleAgentProgress(data);
        break;
      case 'build_progress':
        this.handleBuildProgress(data);
        break;
      default:
        console.warn('Unknown message type:', type);
    }
  }

  /**
   * Handle presence update
   */
  handlePresence(data) {
    const { userId, username, status } = data;

    if (status === 'active') {
      this.presenceMap.set(userId, {
        username,
        status,
        timestamp: data.timestamp,
      });
    } else {
      this.presenceMap.delete(userId);
    }

    this.emit('presence_updated', {
      userId,
      username,
      status,
      allPresence: Array.from(this.presenceMap.entries()),
    });
  }

  /**
   * Handle cursor update
   */
  handleCursor(data) {
    const { userId, username, line, column, fileName } = data;

    this.cursorMap.set(userId, {
      username,
      line,
      column,
      fileName,
      timestamp: data.timestamp,
    });

    this.emit('cursor_updated', {
      userId,
      username,
      line,
      column,
      fileName,
    });
  }

  /**
   * Handle code edit
   */
  handleEdit(data) {
    const { userId, fileName, content, startLine, endLine } = data;

    // Ignore own edits
    if (userId === this.userId) return;

    this.emit('remote_edit', {
      userId,
      fileName,
      content,
      startLine,
      endLine,
    });
  }

  /**
   * Handle agent progress
   */
  handleAgentProgress(data) {
    this.emit('agent_progress', data);
  }

  /**
   * Handle build progress
   */
  handleBuildProgress(data) {
    this.emit('build_progress', data);
  }

  /**
   * Get all active users
   */
  getActiveUsers() {
    return Array.from(this.presenceMap.entries()).map(([userId, data]) => ({
      userId,
      ...data,
    }));
  }

  /**
   * Get user cursor position
   */
  getUserCursor(userId) {
    return this.cursorMap.get(userId);
  }

  /**
   * Register event listener
   */
  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  /**
   * Unregister event listener
   */
  off(event, callback) {
    if (!this.listeners[event]) return;
    this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
  }

  /**
   * Emit event
   */
  emit(event, data) {
    if (!this.listeners[event]) return;
    this.listeners[event].forEach(callback => callback(data));
  }

  /**
   * Disconnect
   */
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
    this.presenceMap.clear();
    this.cursorMap.clear();
  }
}

export default new CollaborationService();
