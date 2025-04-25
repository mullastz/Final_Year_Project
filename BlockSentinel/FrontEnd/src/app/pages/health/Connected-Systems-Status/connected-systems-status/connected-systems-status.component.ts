import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ConnectedSystemStatusService } from '../../../../services/connected-system-status/connected-system-status.service';
import { ConnectedSystemStatus } from '../../../../interface/connected-system-status';


@Component({
  selector: 'app-connected-systems-status',
  imports: [ CommonModule ],
  templateUrl: './connected-systems-status.component.html',
  styleUrl: './connected-systems-status.component.css'
})
export class ConnectedSystemsStatusComponent implements OnInit {
  connectedSystems: ConnectedSystemStatus[] = [];

  constructor(private systemService: ConnectedSystemStatusService) {}

  ngOnInit(): void {
    this.systemService.getConnectedSystems().subscribe(data => {
      this.connectedSystems = data;
    });
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'Running':
        return 'bg-green-500';
      case 'Paused':
        return 'bg-yellow-400';
      case 'Error':
        return 'bg-red-500';
      case 'Stopped':
        return 'bg-gray-500';
      default:
        return 'bg-gray-300';
    }
  }

}
