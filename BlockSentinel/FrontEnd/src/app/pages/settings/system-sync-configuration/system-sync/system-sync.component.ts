import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';  
import { Observable } from 'rxjs';
import { TransformRule } from '../../../../interface/transform-rule';
import { TransformRuleService } from '../../../../services/transform-rule/transform-rule.service';
import { FormsModule } from '@angular/forms';


@Component({
  selector: 'app-system-sync',
  imports: [CommonModule, FormsModule],
  templateUrl: './system-sync.component.html',
  styleUrls: ['./system-sync.component.css'] 
})
export class SystemSyncComponent implements OnInit {
  registeredSystems: string[] = [];
  fullSystemData: any[] = [];
  selectedSystem: string = 'All Systems';
  selectedSystemDetails: any = null;
  syncFrequency: string = 'real-time'; 
  rules: TransformRule[] = [];
  openDropdownId: string | null = null; 
  noTransformEnabled: boolean = false;


  dropdownOpenSystemSelect: boolean = false;
  dropdownOpenSyncLogic: boolean = false;

  sanitizeName(name: string): string {
    return name.replace(/\s+/g, '');
  }
  

  constructor(private http: HttpClient,
    private ruleService: TransformRuleService
  ) {}

  ngOnInit(): void {
    this.loadRegisteredSystems();
    this.loadRules();
  }

  loadRules() {
    this.ruleService.getAll().subscribe(data => this.rules = data);
  }

  toggleDropdown(id: string) {
    this.openDropdownId = this.openDropdownId === id ? null : id;
  }

  editRule(rule: TransformRule) {
    // open inline form (to be implemented)
    console.log('Editing rule:', rule);
  }

  removeRule(id: string) {
    this.ruleService.delete(id).subscribe(() => this.loadRules());
  }

  loadRegisteredSystems(): void {
    this.http.get<any[]>('http://localhost:3000/systems').subscribe({
      next: (systems) => {
        this.fullSystemData = systems;
        this.registeredSystems = systems.map(system => system.name);
        this.updateSelectedSystem(); // Initialize detail view
      },
      error: (err) => {
        console.error('Error loading systems:', err);
        this.registeredSystems = ['System A', 'System B'];
        this.fullSystemData = [];
      }
    });
  }

  toggleDropdownSystemSelect(): void {
    this.dropdownOpenSystemSelect = !this.dropdownOpenSystemSelect;
  }

  toggleDropdownSyncLogic(): void {
    this.dropdownOpenSyncLogic = !this.dropdownOpenSyncLogic;
  }

  onSystemSelect(system: string): void {
    this.selectedSystem = system;
    this.dropdownOpenSystemSelect = false;
    this.dropdownOpenSyncLogic = false;
    this.updateSelectedSystem();
  }

  onFrequencyChange(value: string): void {
    this.syncFrequency = value;
  }

  updateInterval(): void {
    console.log('Updating Sync Configuration...');
    console.log('System:', this.selectedSystem);
    console.log('Frequency:', this.syncFrequency);

    const payload = {
      system: this.selectedSystem,
      syncFrequency: this.syncFrequency,
    };

    this.http.put('http://localhost:3000/systems/updateSync', payload).subscribe({
      next: () => alert('Sync interval updated successfully!'),
      error: (err) => {
        console.error('Failed to update sync interval:', err);
        alert('Failed to update sync interval.');
      }
    });
  }

  updateSelectedSystem(): void {
    this.selectedSystemDetails = this.fullSystemData.find(
      (system) => system.name === this.selectedSystem
    );
  }

  get syncTarget(): string {
    if (!this.selectedSystemDetails) return '';
    const sanitized = this.selectedSystemDetails.name.replace(/\s+/g, '');
    return `Blockchain Ledger /${sanitized}/`;
  }
}
