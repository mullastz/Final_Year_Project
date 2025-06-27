import { Component, OnInit } from '@angular/core';
import { Alert } from '../../interface/alert';
import { AlertService } from '../../services/alert/alert.service';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { FormsModule } from '@angular/forms';


@Component({
  selector: 'app-alert-notification',
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './dashboard-aleart.component.html',
})
export class DashboardAleartComponent implements OnInit {
  alerts: Alert[] = [];
  selectedAlert: any = null;
  searchText: string = '';

  constructor(private alertService: AlertService) {}

  ngOnInit(): void {
    this.alertService.getAlerts().subscribe((data) => {
      this.alerts = data;
    });
  }

  openModal(alert: Alert) {
    this.selectedAlert = alert;
  }

  closeModal() {
    this.selectedAlert = null;
  }

  filteredAlerts(): Alert[] {
    const term = this.searchText.toLowerCase();
    return this.alerts.filter(
      (alert) =>
        alert.severity.toLowerCase().includes(term) ||
        alert.message.toLowerCase().includes(term) ||
        alert.date.toLowerCase().includes(term) ||
        alert.time.toLowerCase().includes(term) ||
        alert.systemId.toLowerCase().includes(term)
    );
  }
  
    downloadPDF(): void {
      const doc = new jsPDF();
      doc.text('Alert Notification Report', 14, 14);
      autoTable(doc, {
        startY: 20,
        head: [['Date & Time', 'Severity', 'Alert Message', 'System ID']],
        body: this.alerts.map(alert => [
          `${alert.date} ${alert.time}`,
          alert.severity,
          alert.message,
          alert.systemId
        ]),
      });
      doc.save('alert-notification.pdf');
    }
    
  }

