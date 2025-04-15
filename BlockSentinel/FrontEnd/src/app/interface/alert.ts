export interface Alert {
    severity: 'Critical' | 'Warning' | 'Info';
    message: string;
    date: string;      // format: YYYY-MM-DD
    time: string;      // format: HH:MM:SS
    status: 'Resolved' | 'Unresolved';
  }
  