import { ActivatedRoute } from '@angular/router';
import { SystemService } from '../../../services/registered-system/registered-system.service';
import { RegisteredSystem } from '../../../interface/registered-system';

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Alert } from '../../../interface/alert';
import { AlertService } from '../../../services/alert/alert.service';
import { DataRecord } from '../../../interface/data-record';
import { DataRecordService } from '../../../services/data-record/data-record.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-system-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './system-detail.component.html',
  styleUrls: ['./system-detail.component.css']
})
export class SystemDetailComponent implements OnInit {
  system: RegisteredSystem | null = null;
  alertNotifications: Alert[] = [];
  dataRecords: DataRecord[] = [];

  showDownloadDropdown = false;
  showFilterDropdown = false;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private systemService: SystemService,
    private alertService: AlertService,
    private dataRecordService: DataRecordService
  ) {}

  toggleDownloadDropdown() {
    this.showDownloadDropdown = !this.showDownloadDropdown;
  }

  toggleFilterDropdown() {
    this.showFilterDropdown = !this.showFilterDropdown;
  }

  goToLedgerDetail(systemId: string, batchId: string) {
    this.router.navigate(['/dashboard-pages/ledger-detail', systemId, batchId]);
  }

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) return;

    // Fetch system details
    this.systemService.getSystemById(id).subscribe({
      next: (data) => {
        this.system = data;
      },
      error: (err) => {
        console.error('[System] Failed to fetch system:', err);
        this.system = null;
      }
    });

    // Fetch alerts (ignore CORS error if it fails)
    this.alertService.getAlerts().subscribe({
      next: (alerts: Alert[]) => {
        this.alertNotifications = alerts.filter(alert => alert.systemId === id);
      },
      error: (err) => {
        console.warn('[Alert] Failed to fetch alerts (expected if using mock):', err);
        this.alertNotifications = [];  // fallback to empty
      }
    });

    // Fetch data records (this must not fail silently)
    this.dataRecordService.getDataRecords(id).subscribe({
      next: (records: DataRecord[]) => {
        console.log('[DataRecord] Fetched records:', records);
        this.dataRecords = records || [];
      },
      error: (err) => {
        console.error('[DataRecord] Failed to fetch records:', err);
        this.dataRecords = [];
      }
    });
    
  }
}
