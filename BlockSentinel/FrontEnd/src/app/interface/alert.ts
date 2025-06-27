export interface Alert {
  id: string;
  timestamp?: string;   // raw timestamp string if available
  date: string;         // extracted from timestamp
  time: string;         // extracted from timestamp
  systemId: string;
  user?: string;
  event_type?: string;
  message: string;      // maps from description
  severity: string;
  source?: string;
  metadata?: any;
}
