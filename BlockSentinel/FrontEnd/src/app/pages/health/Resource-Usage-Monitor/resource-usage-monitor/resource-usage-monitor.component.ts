import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NgApexchartsModule } from 'ng-apexcharts';
import { ResourceUsageService } from '../../../../services/resource-usage/resource-usage.service';
import { ResourceUsage } from '../../../../interface/resource-usage';

@Component({
  selector: 'app-resource-usage-monitor',
  standalone: true,
  imports: [CommonModule, NgApexchartsModule],
  templateUrl: './resource-usage-monitor.component.html',
})
export class ResourceUsageMonitorComponent implements OnInit {
  usageData: ResourceUsage[] = [];

  constructor(private usageService: ResourceUsageService) {}

  ngOnInit(): void {
    this.usageService.getResourceUsage().subscribe(data => {
      this.usageData = data;
    });
  }

  getChartSeries(resource: ResourceUsage) {
    return [
      {
        name: `${resource.type} Usage`,
        data: resource.data.map(d => d.usagePercent),
      },
    ];
  }

  getCategories(resource: ResourceUsage) {
    return resource.data.map(d => d.timestamp);
  }

  getChartOptions(): Partial<{
    chart: ApexChart;
    stroke: ApexStroke;
    xaxis: ApexXAxis;
    dataLabels: { enabled: boolean };
  }> {
    return {
      chart: {
        type: 'line',
        height: 350,
      },
      stroke: {
        curve: 'smooth',
        width: 3,
        colors: ['#29FB05'], // Set your bright green line color here
      },
      xaxis: {
        categories: [], // will be set dynamically when you bind in template
      },
      dataLabels: {
        enabled: false,
      },
    };
  }
}
