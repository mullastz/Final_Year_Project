import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginPageComponent } from './pages/LoginPage/login-page/login-page.component';
import { DashboardOverviewComponent } from './pages/dashboard-overview/dashboard-overview.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { DashboardActivityComponent } from './pages/dashboard-activity/dashboard-activity.component';
import { DashboardAleartComponent } from './pages/dashboard-aleart/dashboard-aleart.component';
import { OtpVerificationComponent } from './pages/otp-verification/otp-verification.component';
import { DashboardPagesComponent } from './pages/dashboard-pages/dashboard-pages.component';
import { RegistrationComponent } from './pages/registration/registration.component';
import { ManagementComponent } from './pages/management/management.component';
import { LogsComponent } from './pages/logs/logs.component';
import { SettingsComponent } from './pages/settings/settings.component';
import { HealthComponent } from './pages/health/health.component';
import { SyncStatusComponent } from './pages/sync-status/sync-status.component';
import { SystemDetailComponent } from './pages/system-detail/system-detail/system-detail.component';
import { LedgerDetailComponent } from './pages/ledger-detail/ledger-detail.component';
import { AdminProfileComponent } from './pages/settings/admin-profile/admin-profile/admin-profile.component';
import { SystemSyncComponent } from './pages/settings/system-sync-configuration/system-sync/system-sync.component';  
import { DataBackupComponent } from './pages/settings/data-export-backup-&-logs/data-backup/data-backup.component';
import { AdvancedConfigurationComponent } from './pages/settings/advanced-configuration/advanced-configuration/advanced-configuration.component';
import { AddNewAdminComponent } from './pages/settings/add-new-admin/add-new-admin.component';
import { SystemHealthOverviewComponent } from './pages/health/System-Health-Overview/system-health-overview/system-health-overview.component';
import { ResourceUsageMonitorComponent } from './pages/health/Resource-Usage-Monitor/resource-usage-monitor/resource-usage-monitor.component';
import { ConnectedSystemsStatusComponent } from './pages/health/Connected-Systems-Status/connected-systems-status/connected-systems-status.component';
import { AlertsNotificationsComponent } from './pages/health/ Alerts-Notifications/alerts-notifications/alerts-notifications.component';
import { AuthGuard } from './guards/auth.guard';




export const routes: Routes = [

    {
      path: '',
      pathMatch: 'full',
      component: LoginPageComponent,
    },

    {
      path: 'otp-verification',
      component: OtpVerificationComponent,
    },
  
    {
      path: 'dashboard',
      component: DashboardComponent,
      canActivate: [AuthGuard], 
      children: [
        { path: '', redirectTo: 'overview', pathMatch: 'full' },
        { path: 'overview', component: DashboardOverviewComponent },
        { path: 'alert', component: DashboardAleartComponent },
        { path: 'activity', component: DashboardActivityComponent },
      ]
    },

    {
      path: 'dashboard-pages',
      component: DashboardPagesComponent,
      children: [
        { path: '', redirectTo: 'registration', pathMatch: 'full' },
        { path: 'registration', component: RegistrationComponent },
        { path: 'management', component: ManagementComponent },
        { path: 'logs', component: LogsComponent },
        { path: 'settings', component: SettingsComponent,
          children: [
            { path: 'admin-profile', component: AdminProfileComponent},
            { path: 'system-sync', component: SystemSyncComponent },
            { path: 'data-backup', component: DataBackupComponent },
            { path: 'advanced-config', component: AdvancedConfigurationComponent },
            { path: '', redirectTo: 'admin-profile', pathMatch: 'full' },
            { path: 'add-new-admin', component: AddNewAdminComponent }
          ]
         },
        { path: 'health', component: HealthComponent,
          children: [
            { path: 'system-health-overview', component: SystemHealthOverviewComponent },
            { path: 'resource-usage-monitor', component: ResourceUsageMonitorComponent },
            { path: 'connected-system-status', component: ConnectedSystemsStatusComponent },
            { path: 'alert-notification', component: AlertsNotificationsComponent },
            { path: '', redirectTo: 'system-health-overview', pathMatch: 'full' },
          ]
         },
        { path: 'sync-status', component: SyncStatusComponent },
        { path: 'system-detail/:id', component: SystemDetailComponent },
        { path: 'ledger-detail/:systemId/:batchId', component: LedgerDetailComponent },

      ]
    },
  
  
    { path: '**', redirectTo: '' }
  
  ];
  
  @NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
  })
  export class AppRoutingModule {}
  
  