import { Component, OnInit } from '@angular/core';
import { SyncStatusService } from '../../services/sync-summary/sync-summary.service';
import { SyncSummary } from '../../interface/sync-summary';

@Component({
  selector: 'app-sync-status',
  templateUrl: './sync-status.component.html',
  styleUrls: ['./sync-status.component.css']
})
export class SyncStatusComponent implements OnInit {
  syncSummary!: SyncSummary;

  constructor(private syncService: SyncStatusService) {}

  ngOnInit(): void {
    this.syncService.getSyncSummary().subscribe(data => {
      this.syncSummary = data;
    });
  }
}
