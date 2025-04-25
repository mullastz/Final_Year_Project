import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AlertNotificationService } from '../../../../services/alert-notification/alert-notification.service';
import { AlertNotification } from '../../../../interface/alerts-notification';

@Component({
  selector: 'app-alerts-notifications',
  imports: [ CommonModule ],
  templateUrl: './alerts-notifications.component.html',
  styleUrl: './alerts-notifications.component.css'
})
export class AlertsNotificationsComponent implements OnInit {
  alerts: AlertNotification[] = [];

  constructor(private alertService: AlertNotificationService) {}

  ngOnInit(): void {
    this.alertService.getAlerts().subscribe(data => {
      this.alerts = data;
    });
  }

  getSeverityColor(severity: string): string {
    switch (severity) {
      case 'low':
        return 'bg-blue-400';
      case 'medium':
        return 'bg-yellow-400';
      case 'high':
        return 'bg-orange-500';
      case 'critical':
        return 'bg-red-600';
      default:
        return 'bg-gray-300';
    }
  }

  handleAction(action: string, alertItem: AlertNotification): void {
    // Implement action logic here if needed
    alert(`Performing "${action}" for alert: ${alertItem.message}`);
  }
}