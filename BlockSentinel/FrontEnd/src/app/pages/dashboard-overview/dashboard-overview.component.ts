import { Component, OnInit } from '@angular/core';
import { SystemService } from '../../services/registered-system/registered-system.service';
import { RegisteredSystem } from '../../interface/registered-system';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { provideCharts, withDefaultRegisterables } from 'ng2-charts';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { ChartConfiguration } from 'chart.js';
import { TransactionService } from '../../services/transaction.service';
import { Transaction } from '../../interface/transaction';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-dashboard-overview',
  standalone: true,
  imports: [CommonModule, RouterModule, BaseChartDirective, FormsModule, HttpClientModule],
  providers: [provideCharts(withDefaultRegisterables())],
  templateUrl: './dashboard-overview.component.html'
})
export class DashboardOverviewComponent implements OnInit {
  systems: RegisteredSystem[] = [];
  transaction: Transaction[] = [];
  showFilterPanel: boolean = false;


  isMenuBarOpen: boolean = true;
  isDownloadDropdownOpen: boolean = false;
  hoveredCard: string | null = null;
  openMenu: string | null = null;

  totalTransactions: number = 0;
  successTransactions: number = 0;
  failedTransactions: number = 0;
  activeUsers: number = 0;
  failedLogins: number = 0;
  uptime: number = 0;

  constructor(
    private systemService: SystemService,
    private transactionService: TransactionService,
    private http: HttpClient 
  ) {}

  ngOnInit(): void {
    this.systemService.getRegisteredSystems().subscribe({
      next: (data) => this.systems = data,
      error: (err) => console.error('Error fetching systems:', err)
    });

    this.transactionService.getTransaction().subscribe({
      next: (data) => this.transaction = data,
      error: (err) => console.error('Error fetching transactions:', err)
    });

    this.transactionService.getAuditSummary().subscribe({
      next: (summary) => {
        this.totalTransactions = summary.total_transactions;
        this.successTransactions = summary.success_transactions;
        this.failedTransactions = summary.failed_transactions;
        this.activeUsers = summary.active_users;
        this.failedLogins = summary.failed_logins;
        this.uptime = summary.uptime;  // if available
      },
      error: (err) => console.error('Error fetching summary:', err)
    });

    this.startHealthMonitoring(); // 👈 add this
}

startHealthMonitoring(): void {
  setInterval(() => {
    this.http.get<{ cpu: number, memory: number }>('http://localhost:8000/auditlog/health-monitoring/')
      .subscribe((data: { cpu: number, memory: number }) => {
        const now = new Date().toLocaleTimeString();

        // Add latest data and keep last 10 entries
        this.lineChartData.labels?.push(now);
        if (this.lineChartData.labels!.length > 10) {
          this.lineChartData.labels!.shift();
        }

        this.lineChartData.datasets[0].data.push(data.memory);
        this.lineChartData.datasets[1].data.push(data.cpu);

        if (this.lineChartData.datasets[0].data.length > 10) {
          this.lineChartData.datasets[0].data.shift();
          this.lineChartData.datasets[1].data.shift();
        }
      });
  }, 5000); // update every 5 seconds
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

  // Health Monitoring Chart Data
  lineChartData: ChartConfiguration<'line'>['data'] = {
    labels: ['00:00', '01:00', '02:00', '03:00', '04:00'],
    datasets: [
      {
        label: 'Memory Usage',
        data: [30, 40, 35, 50, 45],
        borderColor: '#FCAF08',
        backgroundColor: 'rgba(252, 175, 8, 0.2)', 
        fill: true, 
        borderWidth: 2, 
        tension: 0.4,
        pointRadius: 3,
        pointBackgroundColor: '#FCAF08'
      },
      {
        label: 'CPU Usage',
        data: [25, 30, 20, 40, 35],
        borderColor: '#29FB05',
        backgroundColor: 'rgba(41, 251, 5, 0.2)', 
        fill: true,
        borderWidth: 2,
        tension: 0.4,
        pointRadius: 3,
        pointBackgroundColor: '#29FB05'
      }
    ]
    
  };

  

  lineChartOptions: ChartConfiguration<'line'>['options'] = {
    responsive: true,
    plugins: {
      legend: {
        labels: {
          color: 'white'
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: 'white'
        }
      },
      y: {
        ticks: {
          color: 'white'
        }
      }
    }
  };

  filter = {
    function: '',
    status: '',
    systemOrTable: '',
    startDate: '',
    endDate: ''
  };
  

  exportToPDF(): void {
    const doc = new jsPDF();
    autoTable(doc, {
      head: [[
        'Tx Hash', 'Timestamp', 'System ID', 'Table ID',
        'Function', 'Action Type', 'Gas Used', 'Block #', 'Status', 'User'
      ]],
      body: this.transaction.map(txn => [
        txn.tx_hash,
        txn.timestamp,
        txn.system_id || '-',
        txn.table_id || '-',
        txn.function_called,
        txn.action_type,
        txn.gas_used,
        txn.block_number,
        txn.status,
        txn.performed_by || 'System'
      ]),
      styles: { fontSize: 8 }
    });

    doc.save('blockchain_transaction_log.pdf');
  }

  get filteredTransactions(): Transaction[] {
    return this.transaction.filter(txn => {
      const matchesFunction = txn.function_called.toLowerCase().includes(this.filter.function.toLowerCase());
      const matchesStatus = this.filter.status === '' || txn.status === this.filter.status;
      const matchesSystemOrTable =
        this.filter.systemOrTable === '' ||
        (txn.system_id && txn.system_id.toLowerCase().includes(this.filter.systemOrTable.toLowerCase())) ||
        (txn.table_id && txn.table_id.toLowerCase().includes(this.filter.systemOrTable.toLowerCase()));
  
      // Date range filtering (txn.timestamp must be in ISO format)
      const txnDate = new Date(txn.timestamp);
      const start = this.filter.startDate ? new Date(this.filter.startDate) : null;
      const end = this.filter.endDate ? new Date(this.filter.endDate) : null;
      const matchesDate =
        (!start || txnDate >= start) &&
        (!end || txnDate <= end);
  
      return matchesFunction && matchesStatus && matchesSystemOrTable && matchesDate;
    });
  }
  
}
