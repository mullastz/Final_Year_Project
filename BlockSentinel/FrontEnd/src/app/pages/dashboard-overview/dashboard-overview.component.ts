import { Component, OnInit } from '@angular/core';
import { SystemService } from '../../services/registered-system/registered-system.service';
import { RegisteredSystem } from '../../interface/registered-system';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { provideCharts, withDefaultRegisterables } from 'ng2-charts';

import { RouterModule } from '@angular/router';
import { ChartConfiguration } from 'chart.js';
import { TransactionService } from '../../services/transaction.service';
import { Transaction } from '../../interface/transaction';

@Component({
  selector: 'app-dashboard-overview',
  standalone: true,
  imports: [CommonModule, RouterModule, BaseChartDirective], 
  providers: [provideCharts(withDefaultRegisterables())],
  templateUrl: './dashboard-overview.component.html'
})
export class DashboardOverviewComponent implements OnInit {
  systems: RegisteredSystem[] = [];
  isMenuBarOpen: boolean = true;

  hoveredCard: string | null = null;
  openMenu: string | null = null;
  transaction: Transaction[] = [];


  constructor(private systemService: SystemService,
              private transactionService: TransactionService

  ) {}

  ngOnInit(): void {
    this.systemService.getRegisteredSystems().subscribe((data) => {
      this.systems = data;
    });
    
    this.transactionService.getTransaction().subscribe((data) => {
      this.transaction = data;
    });
  }

  toggleMenu(id: string): void {
    this.openMenu = this.openMenu === id ? null : id;
  }

  isDownloadDropdownOpen: boolean = false;

toggleDownloadDropdown(): void {
  this.isDownloadDropdownOpen = !this.isDownloadDropdownOpen;
}


  // Health Monitoring Chart Data
  lineChartData: ChartConfiguration<'line'>['data'] = {
    labels: ['00:00', '01:00', '02:00', '03:00', '04:00'],
    datasets: [
      {
        label: 'Memory Usage',
        data: [30, 40, 35, 50, 45],
        borderColor: '#FCAF08',
        backgroundColor: 'transparent',
        fill: false,
        tension: 0.4
      },
      {
        label: 'CPU Usage',
        data: [25, 30, 20, 40, 35],
        borderColor: '#29FB05',
        backgroundColor: 'transparent',
        fill: false,
        tension: 0.4
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

  // System Status Data
  uptime = 80.8;
  totalTransactions = 1200;
  successTransactions = 98;
  failedTransactions = 22;
  activeUsers = 15;
  failedLogins = 3;
}
