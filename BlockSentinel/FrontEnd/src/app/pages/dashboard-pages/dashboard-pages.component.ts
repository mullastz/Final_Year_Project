import { Component } from '@angular/core';
import { MenuBarComponent } from "../menu-bar/menu-bar.component";
import { HeaderComponent } from "../header/header.component";
import { CommonModule } from "@angular/common";
import { RouterModule } from "@angular/router";

@Component({
  selector: 'app-dashboard-pages',
  imports: [MenuBarComponent, HeaderComponent, CommonModule, RouterModule],
  templateUrl: './dashboard-pages.component.html',
  styleUrl: './dashboard-pages.component.css'
})
export class DashboardPagesComponent {

}
