import { Component, OnInit } from '@angular/core';
import { Activity } from '../../interface/activity';
import { ActivityService } from '../../services/activity/activity.service';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-activity-log',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './dashboard-activity.component.html'
})
export class DashboardActivityComponent implements OnInit {
  activities: Activity[] = [];
  searchText: string = '';

  constructor(private activityService: ActivityService) {}

  ngOnInit(): void {
    this.activityService.getActivities().subscribe(data => {
      this.activities = data;
    });
  }

  filteredActivities(): Activity[] {
    const term = this.searchText.toLowerCase();
    return this.activities.filter(act =>
      act.timestamp.toLowerCase().includes(term) ||
      act.time.toLowerCase().includes(term) ||
      act.user?.toLowerCase().includes(term) ||
      act.action.toLowerCase().includes(term) ||
      act.affectedData.toLowerCase().includes(term) ||
      act.status.toLowerCase().includes(term)
    );
  }

  downloadPDF(): void {
    const doc = new jsPDF();
    doc.text('Activity Log Report', 14, 14);
    autoTable(doc, {
      startY: 20,
      head: [['Timestamp', 'User', 'Action', 'Affected Data / System', 'System ID']],
      body: this.filteredActivities().map(act => [
        `${act.timestamp}, ${act.time}`,
        act.user || '',
        act.action,
        act.affectedData,
        act.status
      ]),
    });
    doc.save('activity-log.pdf');
  }
}
