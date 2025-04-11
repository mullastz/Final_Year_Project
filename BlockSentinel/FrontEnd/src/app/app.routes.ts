import { Routes } from '@angular/router';
import { LoginPageComponent } from './pages/LoginPage/login-page/login-page.component';
import { DashboardOverviewComponent } from './pages/dashboard-overview/dashboard-overview.component';


export const routes: Routes = [

    { path: '', 
        pathMatch: 'full',
        component: LoginPageComponent, 
    }, 

    {
        path: 'dashboard-overview',
        component: DashboardOverviewComponent,
    },

    
];
