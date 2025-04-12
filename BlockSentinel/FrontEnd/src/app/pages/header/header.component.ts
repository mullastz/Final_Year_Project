import { Component } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-header',
  imports: [CommonModule, RouterLink,],
  templateUrl: './header.component.html',
  styleUrl: './header.component.css',
  standalone: true
})
export class HeaderComponent {
  currentPage: string = '';
  showDropdown: boolean = false;

  constructor(private router: Router) {
    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        const routeParts = event.urlAfterRedirects.split('/');
        this.currentPage = routeParts[routeParts.length - 1].replace('-', ' ');
        this.currentPage = this.capitalize(this.currentPage || 'Dashboard');
      }
    });
  }

  capitalize(text: string): string {
    return text.charAt(0).toUpperCase() + text.slice(1);
  }

  toggleDropdown() {
    this.showDropdown = !this.showDropdown;
  }
}
