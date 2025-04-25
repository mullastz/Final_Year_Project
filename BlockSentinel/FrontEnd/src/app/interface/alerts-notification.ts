export interface AlertNotification {
    id: number;
    severity: 'low' | 'medium' | 'high' | 'critical';
    message: string;
    timestamp: string;
    actionType: 'view' | 'retry' | 'dismiss';
  }
  