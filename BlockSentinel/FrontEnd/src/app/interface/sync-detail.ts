export interface SyncDetail {
  id: number;
  dateTime: string;
  system: string;
  recordsSynced: number;
  status: string;
  ledgerHash: string;
  syncedBy: string;
  affectedTables: string;
  notes: string;
}
