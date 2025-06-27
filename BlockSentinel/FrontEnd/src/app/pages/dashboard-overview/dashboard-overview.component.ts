import { Component, OnInit } from '@angular/core';
import { SystemService } from '../../services/registered-system/registered-system.service';
import { RegisteredSystem } from '../../interface/registered-system';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { TransactionService } from '../../services/transaction.service';
import { Transaction } from '../../interface/transaction';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { FormsModule } from '@angular/forms';

import {
  ApexAxisChartSeries,
  ApexChart,
  ApexXAxis,
  ApexStroke,
  ApexDataLabels,
  ApexYAxis,
  ApexLegend,
  ApexTooltip,
  NgApexchartsModule
} from 'ng-apexcharts';
import { NgxApexchartsModule } from 'ngx-apexcharts';

@Component({
  selector: 'app-dashboard-overview',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, HttpClientModule, NgApexchartsModule],
  templateUrl: './dashboard-overview.component.html',
})
export class DashboardOverviewComponent implements OnInit {
  systems: RegisteredSystem[] = [];
  transaction: Transaction[] = [];
  showFilterPanel: boolean = false;

  isMenuBarOpen = true;
  isDownloadDropdownOpen = false;
  hoveredCard: string | null = null;
  openMenu: string | null = null;

  totalTransactions = 0;
  successTransactions = 0;
  failedTransactions = 0;
  activeUsers = 0;
  failedLogins = 0;
  uptime = 0;

  healthChartOptions: {
    series: ApexAxisChartSeries;
    chart: ApexChart;
    xaxis: ApexXAxis;
    stroke: ApexStroke;
    colors: string[];
    dataLabels: ApexDataLabels;
    yaxis: ApexYAxis;
    legend: ApexLegend;
    tooltip: ApexTooltip;
  };

  constructor(
    private systemService: SystemService,
    private transactionService: TransactionService,
    private http: HttpClient
  ) {
    this.healthChartOptions = {
      series: [
        { name: 'Memory Usage', data: [] },
        { name: 'CPU Usage', data: [] }
      ],
      chart: {
        height: 250,
        type: 'line',
        zoom: { enabled: false },
        toolbar: { show: false }
      },
      colors: ['#FCAF08', '#29FB05'],
      stroke: { curve: 'smooth', width: 3 },
      dataLabels: { enabled: false },
      xaxis: { categories: [] },
      yaxis: {
        min: 0,
        max: 100,
        labels: { formatter: (val) => val + '%', style: { colors: ['#fff'] } }
      },
      legend: { labels: { colors: '#fff' } },
      tooltip: { enabled: true }
    };
  }

  ngOnInit(): void {
    this.systemService.getRegisteredSystems().subscribe({
      next: (data) => (this.systems = data),
      error: (err) => console.error('Error fetching systems:', err),
    });

    this.transactionService.getTransaction().subscribe({
      next: (data) => (this.transaction = data),
      error: (err) => console.error('Error fetching transactions:', err),
    });

    this.transactionService.getAuditSummary().subscribe({
      next: (summary) => {
        this.totalTransactions = summary.total_transactions;
        this.successTransactions = summary.success_transactions;
        this.failedTransactions = summary.failed_transactions;
        this.activeUsers = summary.active_users;
        this.failedLogins = summary.failed_logins;
        this.uptime = summary.uptime;
      },
      error: (err) => console.error('Error fetching summary:', err),
    });

    this.startHealthMonitoring();
  }

  startHealthMonitoring(): void {
    setInterval(() => {
      this.http.get<{ cpu: number; memory: number }>('http://localhost:8000/auditlog/health-monitoring/').subscribe((data) => {
        const now = new Date().toLocaleTimeString();

        const categories = this.healthChartOptions.xaxis?.categories!;
        const memData = this.healthChartOptions.series![0].data as number[];
        const cpuData = this.healthChartOptions.series![1].data as number[];

        categories.push(now);
        memData.push(data.memory);
        cpuData.push(data.cpu);

        if (categories.length > 10) {
          categories.shift();
          memData.shift();
          cpuData.shift();
        }
      });
    }, 10000);
  }

  toggleMenu(id: string): void {
    this.openMenu = this.openMenu === id ? null : id;
  }

  toggleDownloadDropdown(): void {
    this.isDownloadDropdownOpen = !this.isDownloadDropdownOpen;
  }

  toggleFilterPanel(): void {
    this.showFilterPanel = !this.showFilterPanel;
  }

  filter = {
    function: '',
    status: '',
    systemOrTable: '',
    startDate: '',
    endDate: '',
  };

  exportToPDF(): void {
    const doc = new jsPDF();
    autoTable(doc, {
      head: [
        [
          'Tx Hash',
          'Timestamp',
          'System ID',
          'Table ID',
          'Function',
          'Action Type',
          'Gas Used',
          'Block #',
          'Status',
          'User',
        ],
      ],
      body: this.transaction.map((txn) => [
        txn.tx_hash,
        txn.timestamp,
        txn.system_id || '-',
        txn.table_id || '-',
        txn.function_called,
        txn.action_type,
        txn.gas_used,
        txn.block_number,
        txn.status,
        txn.performed_by || 'System',
      ]),
      styles: { fontSize: 8 },
    });

    doc.save('blockchain_transaction_log.pdf');
  }

  get filteredTransactions(): Transaction[] {
    return this.transaction.filter((txn) => {
      const matchesFunction = txn.function_called
        .toLowerCase()
        .includes(this.filter.function.toLowerCase());
      const matchesStatus =
        this.filter.status === '' || txn.status === this.filter.status;
      const matchesSystemOrTable =
        this.filter.systemOrTable === '' ||
        (txn.system_id &&
          txn.system_id
            .toLowerCase()
            .includes(this.filter.systemOrTable.toLowerCase())) ||
        (txn.table_id &&
          txn.table_id
            .toLowerCase()
            .includes(this.filter.systemOrTable.toLowerCase()));

      const txnDate = new Date(txn.timestamp);
      const start = this.filter.startDate
        ? new Date(this.filter.startDate)
        : null;
      const end = this.filter.endDate ? new Date(this.filter.endDate) : null;
      const matchesDate =
        (!start || txnDate >= start) && (!end || txnDate <= end);

      return (
        matchesFunction && matchesStatus && matchesSystemOrTable && matchesDate
      );
    });
  }
}
