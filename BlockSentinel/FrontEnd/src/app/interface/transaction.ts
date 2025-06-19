export interface Transaction {
  tx_hash: string;
  timestamp: string;
  system_id: string | null;
  table_id: string | null;
  function_called: string;
  action_type: string;
  gas_used: number;
  block_number: number;
  status: 'Success' | 'Fail';
  performed_by: string | null;
}
