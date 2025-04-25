export interface ConnectedSystemStatus {
    system: string;
    status: 'Running' | 'Stopped' | 'Error' | 'Paused';  // or extend as needed
    lastSync: string;
    syncInterval: string;
    errors: number;
  }
  