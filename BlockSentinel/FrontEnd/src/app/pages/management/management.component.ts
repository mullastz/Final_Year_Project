import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { SystemService } from '../../services/registered-system/registered-system.service';
import { RegisteredSystem } from '../../interface/registered-system';

@Component({
  selector: 'app-management',
  imports: [ CommonModule, RouterModule ],
  templateUrl: './management.component.html',
  styleUrl: './management.component.css'
})
export class ManagementComponent {
  systems: RegisteredSystem[] = [];
    isMenuBarOpen: boolean = true;
  
    hoveredCard: string | null = null;
    openMenu: string | null = null;
   
     constructor(private systemService: SystemService,) {}
    
      ngOnInit(): void {
        this.systemService.getRegisteredSystems().subscribe((data) => {
          this.systems = data;
        });
        
      }
    
      toggleMenu(id: string): void {
        this.openMenu = this.openMenu === id ? null : id;
      }
    
      isDownloadDropdownOpen: boolean = false;
    
    toggleDownloadDropdown(): void {
      this.isDownloadDropdownOpen = !this.isDownloadDropdownOpen;
    }
    
    
  

}
