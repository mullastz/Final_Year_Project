// src/app/pages/health/health.module.ts
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NgChartsModule } from 'ng2-charts';
import { ResourceUsageMonitorComponent } from './Resource-Usage-Monitor/resource-usage-monitor/resource-usage-monitor.component';

@NgModule({
  imports: [
    CommonModule,
    NgChartsModule,
    ResourceUsageMonitorComponent
  ],
  exports: [ResourceUsageMonitorComponent]
})
export class HealthModule {}
