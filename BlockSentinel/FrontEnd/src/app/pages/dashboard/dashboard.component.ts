import { Component } from '@angular/core';
import { MenuBarComponent } from "../menu-bar/menu-bar.component";
import { HeaderComponent } from "../header/header.component";
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  imports: [MenuBarComponent, HeaderComponent, CommonModule, RouterLink, RouterModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent {
showFilterDropdown: boolean = false;

  toggleFilterDropdown() {
    this.showFilterDropdown = !this.showFilterDropdown;

}
}
