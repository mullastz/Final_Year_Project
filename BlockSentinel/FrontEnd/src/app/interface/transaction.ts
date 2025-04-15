export interface Transaction {
  transactionId: string;
  timestamp: string;
  systemName: string;
  actionType: string;
  status: 'Success' | 'Failed';
  performedBy: string;
}
