import { Component, OnInit } from '@angular/core';
import { ResourceUsageService } from '../../../../services/resource-usage/resource-usage.service';
import { ResourceUsage } from '../../../../interface/resource-usage';

import { ChartData, ChartOptions, ChartType } from 'chart.js';
import { CommonModule, NgIf, NgFor } from '@angular/common';
import { NgChartsModule } from 'ng2-charts';

@Component({
  selector: 'app-resource-usage-monitor',
  standalone: true,
  imports: [
    CommonModule,
    NgChartsModule,
    NgFor  // ✅ Required for *ngFor to work in template
  ],
  templateUrl: './resource-usage-monitor.component.html',
  styleUrls: ['./resource-usage-monitor.component.css'],
})
export class ResourceUsageMonitorComponent implements OnInit {
  usageData: ResourceUsage[] = [];

  chartConfigs: {
    [key: string]: {
      data: ChartData<'line'>;
      options: ChartOptions<'line'>;
      type: ChartType;
    };
  } = {};

  constructor(private usageService: ResourceUsageService) {}

  ngOnInit(): void {
    this.usageService.getResourceUsage().subscribe((data) => {
      this.usageData = data;
      this.prepareCharts();
    });
  }

  prepareCharts(): void {
    this.usageData.forEach(resource => {
      const labels = resource.data.map(d => new Date(d.timestamp).toLocaleTimeString());
      const usageValues = resource.data.map(d => d.usagePercent);

      this.chartConfigs[resource.type] = {
        data: {
          labels,
          datasets: [
            {
              label: `${resource.type} Usage`,
              data: usageValues,
              borderColor: this.getLineColor(resource.type),
              backgroundColor: 'transparent',
              tension: 0.4
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              labels: { color: 'white' }
            }
          },
          scales: {
            x: { ticks: { color: 'white' } },
            y: { beginAtZero: true, ticks: { color: 'white' } }
          }
        },
        type: 'line'
      };
    });
  }

  getLineColor(type: string): string {
    switch (type) {
      case 'CPU': return '#29FB05';
      case 'Memory': return '#FCAF08';
      case 'Storage': return '#08A2FC';
      case 'Gas': return '#FF6B6B';
      default: return '#ffffff';
    }
  }
}
