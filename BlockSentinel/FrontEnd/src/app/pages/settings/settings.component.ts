import { Component } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.css'],
})
export class SettingsComponent {
  currentRoute: string = '';

  menuItems = [
    { label: 'Admin Profile', route: '/dashboard-pages/settings/admin-profile' },
    { label: 'System Sync Configuration', route: '/dashboard-pages/settings/system-sync' },
    { label: 'Data Export Backup & Logs', route: '/dashboard-pages/settings/data-backup' },
    { label: 'Advanced Configuration', route: '/dashboard-pages/settings/advanced-config' },
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
