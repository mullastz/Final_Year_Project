import { Component } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-health',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './health.component.html',
  styleUrl: './health.component.css'
})
export class HealthComponent {
  currentRoute: string = '';

  menuItems = [
    { label: 'System Health Overview', route: '/dashboard-pages/health/system-health-overview', icon: 'fas fa-heartbeat' },
    { label: 'Resource Usage Monitor', route: '/dashboard-pages/health/resource-usage-monitor', icon: 'fas fa-microchip' },
    { label: 'Connected Systems Status', route: '/dashboard-pages/health/connected-system-status', icon: 'fas fa-network-wired' },
    { label: 'Alerts & Notifications', route: '/dashboard-pages/health/alert-notification', icon: 'fas fa-bell' },
  ];
  

  constructor(private router: Router) {
    this.setCurrentRoute();
    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe(() => this.setCurrentRoute());
  }

  private setCurrentRoute() {
    this.currentRoute = this.router.url;
  }

  navigate(route: string) {
    this.router.navigate([route]);
  }

}
