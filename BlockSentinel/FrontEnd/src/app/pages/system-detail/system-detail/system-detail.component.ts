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
  system!: RegisteredSystem;
  alertNotifications: Alert[] = [];
  dataRecords: DataRecord[] = [];

  showDownloadDropdown = false;
  showFilterDropdown = false;

  toggleDownloadDropdown() {
    this.showDownloadDropdown = !this.showDownloadDropdown;
  }

  toggleFilterDropdown() {
    this.showFilterDropdown = !this.showFilterDropdown;
  }

  goToLedgerDetail(systemId: string, batchId: string) {
    this.router.navigate(['/dashboard-pages/ledger-detail', systemId, batchId]);
  }
  
  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private systemService: SystemService,
    private alertService: AlertService,
    private dataRecordService: DataRecordService
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    this.systemService.getSystemById(id!).subscribe((data) => {
      this.system = data;
    });

    this.alertService.getAlerts().subscribe((alerts: Alert[]) => {
      this.alertNotifications = alerts.filter(alert => alert.systemId === id);
    });

    this.dataRecordService.getDataRecords().subscribe((records: DataRecord[]) => {
      this.dataRecords = records.filter(record => record.systemId === id);
    });

  }
}
