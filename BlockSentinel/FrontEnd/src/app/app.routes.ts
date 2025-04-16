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
        { path: 'settings', component: SettingsComponent },
        { path: 'health', component: HealthComponent },
        { path: 'sync-status', component: SyncStatusComponent },
        { path: 'system-detail/:id', component: SystemDetailComponent }

      ]
    },
  
  
    { path: '**', redirectTo: '' }
  
  ];
  
  @NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
  })
  export class AppRoutingModule {}
  
  