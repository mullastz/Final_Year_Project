import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { SystemService } from '../../services/registered-system/registered-system.service';
import { RegisteredSystem } from '../../interface/registered-system';
import { Router } from '@angular/router';

@Component({
  selector: 'app-management',
  imports: [ CommonModule, RouterModule ],
  templateUrl: './management.component.html',
  styleUrl: './management.component.css',
  providers: [SystemService]
})
export class ManagementComponent {
onCardClick(arg0: string) {
throw new Error('Method not implemented.');
}
  systems: RegisteredSystem[] = [];
    isMenuBarOpen: boolean = true;
  
    hoveredCard: string | null = null;
    openMenu: string | null = null;
   
     constructor(private systemService: SystemService,
      private router: Router,
     ) {}
    
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

    goToSystemDetail(id: string) {
      this.router.navigate(['/dashboard-pages/system-detail', id]);
    }
   
}
