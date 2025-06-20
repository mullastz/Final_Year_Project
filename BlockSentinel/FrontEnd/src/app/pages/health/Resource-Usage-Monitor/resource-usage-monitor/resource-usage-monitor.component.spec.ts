import { Component, OnInit } from '@angular/core';
import { ResourceUsageService } from '../../../../services/resource-usage/resource-usage.service';
import { ResourceUsage } from '../../../../interface/resource-usage';
import { CommonModule } from '@angular/common';
import { NgApexchartsModule } from 'ng-apexcharts';
import {
  ApexAxisChartSeries,
  ApexChart,
  ApexXAxis,
  ApexStroke,
  ApexFill
} from 'ng-apexcharts';

// ✅ Strongly typed interface for chart config per resource
interface ResourceChartData {
  type: string;
  series: ApexAxisChartSeries;
  chart: ApexChart;
  xaxis: ApexXAxis;
  stroke: ApexStroke;
  fill: ApexFill;
  colors: string[];
}

@Component({
  selector: 'app-resource-usage-monitor',
  standalone: true,
  imports: [CommonModule, NgApexchartsModule],
  templateUrl: './resource-usage-monitor.component.html',
  styleUrls: ['./resource-usage-monitor.component.css']
})
export class ResourceUsageMonitorComponent implements OnInit {
  usageData: ResourceChartData[] = [];

  constructor(private usageService: ResourceUsageService) {}

  ngOnInit(): void {
    this.usageService.getResourceUsage().subscribe((data: ResourceUsage[]) => {
      this.usageData = data.map((resource) => {
        const labels = resource.data.map(d =>
          new Date(d.timestamp).toLocaleTimeString()
        );
        const values = resource.data.map(d => d.usagePercent);

        return {
          type: resource.type,
          series: [
            {
              name: `${resource.type} Usage`,
              data: values
            }
          ],
          chart: {
            type: 'line',
            height: 250
          },
          xaxis: {
            categories: labels,
            labels: {
              style: { colors: '#ffffff' }
            }
          },
          stroke: {
            curve: 'smooth',
            width: 2
          },
          fill: {
            type: 'gradient',
            gradient: {
              shade: 'dark',
              type: 'vertical',
              gradientToColors: undefined,
              stops: [0, 100]
            }
          },
          colors: [this.getLineColor(resource.type)]
        };
      });
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
