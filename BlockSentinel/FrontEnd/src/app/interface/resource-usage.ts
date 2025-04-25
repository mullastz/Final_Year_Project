export interface ResourceUsageData {
    timestamp: string;      // e.g., "2025-04-24T10:00:00Z"
    usagePercent: number;   // e.g., 45
  }
  
  export interface ResourceUsage {
    type: 'CPU' | 'Memory' | 'Storage' | 'Gas';
    data: ResourceUsageData[];
  }
  