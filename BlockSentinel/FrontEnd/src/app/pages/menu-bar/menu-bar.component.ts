import { Component } from '@angular/core';
import { CommonModule } from '@angular/common'; 

@Component({
  selector: 'app-menu-bar',
  imports: [CommonModule],
  templateUrl: './menu-bar.component.html',
  styleUrls: ['./menu-bar.component.css']  // Note: it should be "styleUrls" not "styleUrl"
})
export class MenuBarComponent {
  isCollapsed = false;

  toggleSidebar(): void {
    this.isCollapsed = !this.isCollapsed;
  }
}

