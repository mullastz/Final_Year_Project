export interface SystemHealth {
    id: number;
    service: string;
    status: 'Running' | 'Slow Sync' | 'Healthy' | 'Down';
    lastChecked: string;
  }
  