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

}
