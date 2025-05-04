import { Component, OnInit } from '@angular/core';
import { v4 as uuidv4 } from 'uuid'; 
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';



@Component({
  selector: 'app-registration',
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './registration.component.html'
})
export class RegistrationComponent implements OnInit {
  systemId: string = '';
  systemImage: string | ArrayBuffer | File | null = null;

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
  systemName: string = '';
  systemUrl: string = '';
  selectedDataType: string = '';
  selectedSystemType: string = '';


  ngOnInit(): void {
    const fullId = uuidv4(); // generate UUID
    this.systemId = 'SYS-' + fullId.split('-')[0]; // format to SYS-xxxxxxx
  }
  

  onImageUpload(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.systemImage = file; // ⬅️ store the actual File
      const reader = new FileReader();
      reader.onload = () => {
        // Just for preview, not needed for submission
      };
      reader.readAsDataURL(file);
    }
  }
  

constructor(private http: HttpClient) {}

  generateAdminFields(): void {
    this.adminFields = Array.from({ length: this.adminCount }, () => ({ name: '', email: '' }));
  }

  submitRegistration(): void {
    // Ensure required fields are filled
    if (!this.systemName || !this.systemUrl || !this.selectedDataType || !this.selectedSystemType) {
      alert('Please fill in all required fields.');
      return;  // Prevent submission if required fields are missing
    }
  
    const formData = new FormData();
  
    formData.append('display_id', this.systemId);
    formData.append('name', this.systemName);
    formData.append('url', this.systemUrl);
    formData.append('data_type', this.selectedDataType);
    formData.append('system_type', this.selectedSystemType);
    formData.append('num_admins', this.adminCount.toString());
  
    // Only add profile photo if available
    if (this.systemImage instanceof File) {
      formData.append('profile_photo', this.systemImage);
    }
  
    // Handle admins
    this.adminFields.forEach((admin, index) => {
      formData.append(`admins[${index}][name]`, admin.name);
      formData.append(`admins[${index}][email]`, admin.email);
    });
  
    this.http.post('http://127.0.0.1:8000/reg/register-system/', formData).subscribe({
      next: (response: any) => {
        console.log('Registered:', response);
      },
      error: (error) => {
        console.error('Registration failed:', error);
        console.error('Server error details:', error.error);
      }
    });
  }
  
  
}
