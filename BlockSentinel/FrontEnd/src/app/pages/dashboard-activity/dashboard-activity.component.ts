import { Component, OnInit } from '@angular/core';
import { Activity } from '../../interface/activity';
import { ActivityService } from '../../services/activity/activity.service';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-activity-log',
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard-activity.component.html'
})
export class DashboardActivityComponent implements OnInit {
  activities: Activity[] = [];
  isDownloadDropdownOpen = false;

  constructor(private activityService: ActivityService) {}

  ngOnInit(): void {
    this.activityService.getActivities().subscribe(data => {
      this.activities = data;
    });
  }

  toggleDownloadDropdown(): void {
    this.isDownloadDropdownOpen = !this.isDownloadDropdownOpen;
  }
}
