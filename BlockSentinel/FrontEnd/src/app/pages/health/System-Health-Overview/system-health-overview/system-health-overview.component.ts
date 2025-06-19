import { Component, OnInit } from '@angular/core';
import { SystemHealthService } from '../../../../services/system-health/system-health.service';
import { SystemHealth } from '../../../../interface/system-health';
import { CommonModule } from '@angular/common';



@Component({
  selector: 'app-system-health-overview',
  imports: [ CommonModule ],
  templateUrl: './system-health-overview.component.html',
  styleUrl: './system-health-overview.component.css'
})
export class SystemHealthOverviewComponent {
  systemHealthList: SystemHealth[] = [];
  selectedLogs: string[] = [];
  selectedService: string = '';
  isLogModalOpen: boolean = false;


  constructor(private healthService: SystemHealthService) {}

  ngOnInit(): void {
    this.healthService.getSystemHealth().subscribe(data => {
      this.systemHealthList = data;
    });
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'Running':
      case 'Healthy':
        return 'bg-[#29FB05]';
      case 'Slow Sync':
        return 'bg-[#FCAF08]';
      case 'Down':
        return 'bg-[#FB0505]';
      default:
        return 'bg-gray-400';
    }
  }

  getActions(status: string, service: string): string[] {
    if (service === 'Scheduler') return [];
    switch (status) {
      case 'Running':
        return ['Stop'];
      case 'Slow Sync':
        return ['Reconnect', 'View Logs'];
      case 'Healthy':
        return ['View Logs'];
      case 'Down':
        return ['Retry', 'View Logs'];
      default:
        return [];
    }
  }

  handleAction(action: string, service: string): void {
    if (action === 'Retry' || action === 'Reconnect') {
      this.healthService.retryService(service).subscribe({
        next: (res) => {
          // Update UI with new status
          const item = this.systemHealthList.find(s => s.service === res.service);
          if (item) {
            item.status = res.newStatus;
            item.lastChecked = new Date().toISOString();
          }
        },
        error: (err) => {
          console.error(`Failed to ${action} for ${service}:`, err);
        }
      });
    } else if (action === 'View Logs') {
      alert(`🚧 Logs not implemented yet for ${service}`);
    } else if (action === 'Stop') {
      alert(`🛑 Stop command not available for ${service}`);
    }
  }

  viewLogs(service: string): void {
    this.healthService.getServiceLogs(service).subscribe(response => {
      this.selectedLogs = response.logs;
      this.selectedService = service;
      this.isLogModalOpen = true;
    });
  }
  
  stopAgent(): void {
    this.healthService.stopAgent().subscribe({
      next: () => alert('Agent stopped successfully.'),
      error: () => alert('Failed to stop agent.')
    });
  }
  
  closeLogs(): void {
    this.selectedLogs = [];
    this.selectedService = '';
  }

}
