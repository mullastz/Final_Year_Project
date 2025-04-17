import { Component, OnInit } from '@angular/core';
import { SyncStatusService } from '../../services/sync-summary/sync-summary.service';
import { SyncDetailService } from '../../services/sync-detail/sync-detail.service';
import { SyncSummary } from '../../interface/sync-summary';
import { SyncDetail } from '../../interface/sync-detail';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-sync-status',
  imports: [CommonModule, RouterModule],
  templateUrl: './sync-status.component.html',
  styleUrls: ['./sync-status.component.css']
})
export class SyncStatusComponent implements OnInit {
  syncSummary!: SyncSummary;
  showDownloadDropdown = false;
  syncDetails: SyncDetail[] = [];
  selectedSyncDetail: SyncDetail | null = null;

  constructor(
    private syncStatusService: SyncStatusService,
    private syncDetailService: SyncDetailService
  ) {}

  ngOnInit(): void {
    this.syncStatusService.getSyncSummary().subscribe(data => {
      this.syncSummary = Array.isArray(data) ? data[0] : data;
    });

    this.syncDetailService.getSyncDetails().subscribe(data => {
      this.syncDetails = data;
    });
  }

  toggleDownloadDropdown() {
    this.showDownloadDropdown = !this.showDownloadDropdown;
  }

  viewMore(sync: SyncDetail) {
    this.selectedSyncDetail = sync;
  }

  closeDetailCard() {
    this.selectedSyncDetail = null;
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'Success': return '#29FB05';
      case 'Failed': return '#FB0505';
      default: return '#7B7272'; // fallback for other statuses
    }
  }
}
