export interface SystemLog {
  timestamp: string;
  actor: string;
  actionType: string;
  system: string;
  description: string;
  status: 'Success' | 'Alert' | 'Viewed'; 
  systemId: string;
  batchId: string;
  ledgerHash: string;
  relatedData: string;
  linkedAlert: string;
}
