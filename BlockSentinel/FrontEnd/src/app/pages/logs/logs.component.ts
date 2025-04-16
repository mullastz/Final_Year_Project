import { Component, OnInit } from '@angular/core';
import { LogService } from '../../services/system-log/system-log.service'; 
import { SystemLog } from '../../interface/system-log'; 
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-logs',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './logs.component.html'
})
export class LogsComponent implements OnInit {
  logs: SystemLog[] = [];
  showDownloadDropdown = false;
  selectedLog: SystemLog | null = null;

  constructor(private logService: LogService) {}

  ngOnInit(): void {
    this.logService.getLogs().subscribe((data) => {
      this.logs = data;
    });
  }

  toggleDownloadDropdown() {
    this.showDownloadDropdown = !this.showDownloadDropdown;
  }

  viewLogDetail(log: SystemLog) {
    this.selectedLog = log; 
  }

  closeLogDetail() {
    this.selectedLog = null; 
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'Success': return '#29FB05';
      case 'Alert': return '#FB0505';
      case 'Viewed': return '#7B7272';
      default: return '#CCC';
    }
  }
}
