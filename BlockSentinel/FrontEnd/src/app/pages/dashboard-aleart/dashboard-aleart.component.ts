import { Component, OnInit } from '@angular/core';
import { Alert } from '../../interface/alert';
import { AlertService } from '../../services/alert/alert.service';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-alert-notification',
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard-aleart.component.html'
})
export class DashboardAleartComponent implements OnInit {
  alerts: Alert[] = [];
  isDownloadDropdownOpen = false;

  constructor(private alertService: AlertService) {}

  ngOnInit(): void {
    this.alertService.getAlerts().subscribe(data => {
      this.alerts = data;
    });
  }

  toggleDownloadDropdown(): void {
    this.isDownloadDropdownOpen = !this.isDownloadDropdownOpen;
  }
}
