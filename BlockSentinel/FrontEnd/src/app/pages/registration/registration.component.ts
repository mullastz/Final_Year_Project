import { Component, OnInit } from '@angular/core';
import { v4 as uuidv4 } from 'uuid'; 
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-registration',
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './registration.component.html'
})
export class RegistrationComponent implements OnInit {
  systemId: string = '';
  systemImage: string | ArrayBuffer | null = null;

  dataTypes: string[] = [
    'Student Results', 'Patient Records', 'Financial Transactions',
    'Employee Data', 'Government Records', 'Customer Info'
  ];

  systemTypes: string[] = [
    'University System', 'Hospital System', 'Banking System',
    'Government System', 'Corporate Platform'
  ];

  adminCount: number = 1;
  adminFields: { name: string; email: string }[] = [{ name: '', email: '' }];

  ngOnInit(): void {
    this.systemId = uuidv4(); // Auto-generate unique ID
  }

  onImageUpload(event: any): void {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        this.systemImage = reader.result;
      };
      reader.readAsDataURL(file);
    }
  }

  generateAdminFields(): void {
    this.adminFields = Array.from({ length: this.adminCount }, () => ({ name: '', email: '' }));
  }

  submitRegistration(): void {
    // Submit logic here
    console.log('Registration Submitted');
  }
}
