import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginPageComponent } from './pages/LoginPage/login-page/login-page.component';
import { DashboardOverviewComponent } from './pages/dashboard-overview/dashboard-overview.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { DashboardActivityComponent } from './pages/dashboard-activity/dashboard-activity.component';
import { DashboardAleartComponent } from './pages/dashboard-aleart/dashboard-aleart.component';

export const routes: Routes = [

    {
      path: '',
      pathMatch: 'full',
      component: LoginPageComponent,
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
  
    { path: '**', redirectTo: '' }
  
  ];
  
  @NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
  })
  export class AppRoutingModule {}
  
  