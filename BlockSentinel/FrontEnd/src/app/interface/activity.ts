export interface Activity {
    timestamp: string;      // format: YYYY-MM-DD
    time: string;           // format: HH:MM
    user: string;
    action: string;
    affectedData: string;
    status: 'Success' | 'Failed' | 'Warning';
  }
  