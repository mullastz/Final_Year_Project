import { Component, OnInit } from '@angular/core';
import { v4 as uuidv4 } from 'uuid'; 
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { RegistrationService } from '../../services/registration/registration.service';

type ModalStep = 'progress' | 'selectDb' | 'enterCredentials';

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
  registrationFormData: FormData | undefined;
  registeredSystem: any;

  // Modal & Progress State
  showProgressModal = false;
  progressMessage = 'Installing Agent...';
  progressValue = 0;
  step: ModalStep = 'progress';

  // Discovery & DB Selection
  discoveredDatabases: { name: string; type: string }[] = [];
  selectedDatabase: string | null = null;
  dbCredentials = { host: '', port: '', username: '', password: '', extra: '' };

  isRegistering = false;
  isInstallingAgent = false;
  isDiscoveringDatabases = false;
  isDatabaseSelectionVisible = false;

  selectedSystemId: string = '';
  selectedDisplayId: string = '';

  constructor(private http: HttpClient, private registrationService: RegistrationService) {}

  ngOnInit(): void {
    const fullId = uuidv4(); // generate UUID
    this.systemId = 'SYS-' + fullId.split('-')[0]; // format to SYS-xxxxxxx
  }

  onImageUpload(event: any): void {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        this.systemImage = reader.result; // Show preview immediately
      };
      reader.readAsDataURL(file);
      this.systemImage = file; // Also store raw file for upload
    }
  }

  generateAdminFields(): void {
    this.adminFields = Array.from({ length: this.adminCount }, () => ({ name: '', email: '' }));
  }

  private buildFormData(): FormData {
    const formData = new FormData();
    formData.append('display_id', this.systemId);
    formData.append('name', this.systemName);
    formData.append('url', this.systemUrl);
    formData.append('data_type', this.selectedDataType);
    formData.append('system_type', this.selectedSystemType);
    formData.append('num_admins', this.adminCount.toString());

    if (this.systemImage instanceof File) {
      formData.append('profile_photo', this.systemImage);
    }

    this.adminFields.forEach((admin, index) => {
      formData.append(`admins[${index}][name]`, admin.name);
      formData.append(`admins[${index}][email]`, admin.email);
    });

    return formData;
  }

  submitRegistration(): void {
    this.isRegistering = true;
    const formData = this.buildFormData();

    this.registrationService.registerSystem(formData).subscribe({
      next: (response: any) => {
        console.log('Registered:', response);
        this.handleSuccessfulRegistration(response);
        this.startAgentInstallation();
      },
      error: (error) => {
        console.error('Registration failed:', error);
        alert('Registration failed.');
        this.isRegistering = false;
      }
    });
  }

  handleSuccessfulRegistration(response: any): void {
    this.registeredSystem = response;
    this.discoveredDatabases = response.discovered_databases || [];
  }

  startAgentInstallation(): void {
    this.showProgressModal = true;
    this.step = 'progress';
    this.progressValue = 10;
    this.progressMessage = 'Installing agent...';

    this.http.post('http://127.0.0.1:8000/reg/install-agent/', { url: this.systemUrl }).subscribe({
      next: () => {
        this.progressValue = 70;
        this.progressMessage = 'Discovering databases...';
        this.isDiscoveringDatabases = true;

        this.http.get<{ name: string; type: string }[]>(`http://127.0.0.1:8000/reg/discover-databases/?url=${this.systemUrl}`).subscribe({
          next: (dbs) => {
            this.progressValue = 100;
            this.progressMessage = 'Discovery complete.';
            this.discoveredDatabases = Array.isArray(dbs) ? dbs : Object.values(dbs);
            this.step = 'selectDb';
            this.isDiscoveringDatabases = false;
          },
          
          error: (err) => {
            this.progressMessage = 'Failed to discover databases.';
            this.isDiscoveringDatabases = false;
            const errorMsg = err?.error?.detail || 'Unknown error';
            alert('Error discovering databases: ' + errorMsg);
            console.error('DB Discovery failed:', err);
          }
        });
      },
      error: (err) => {
        this.progressMessage = 'Agent installation failed.';
        alert('Agent installation failed. Please try again.');
        console.error('Agent installation error:', err);
        this.isDiscoveringDatabases = false;
      }
    });
  }

  onDatabaseSelectionChange(dbName: string, event: Event) {
    const checkbox = event.target as HTMLInputElement;
    if (checkbox.checked) {
      this.selectedDatabases.add(dbName);
    } else {
      this.selectedDatabases.delete(dbName);
    }
  }
  
  secureDatabases() {
    const agentUrl = 'http://127.0.0.1:8000'; // Replace this with wherever you're storing the system URL
    const dbList = Array.from(this.selectedDatabases).map(name => ({
      name,
      type: this.selectedDbType
    }));
  
    const credentialsMap: any = {};
    this.selectedDatabases.forEach(dbName => {
      credentialsMap[dbName] = {
        host: this.credentials.host,
        port: this.credentials.port,
        username: this.credentials.username,
        password: this.credentials.password
      };
    });
  
    const payload = {
      url: agentUrl,
      db_name: dbList,
      credentials: credentialsMap
    };
  
    this.registrationService. extractData(payload).subscribe({
      next: () => {
        alert('Databases secured successfully!');
      },
      error: () => {
        alert('Failed to secure databases.');
      }
    });
  }

  handleSuccessfulRegistration(response: any): void {
    this.registeredSystem = response;
    this.discoveredDbTypes = response.discovered_databases.map(
      (db: DiscoveredDatabase) => db.type
    );
  }
  

 

  submitDbCredentials(): void {
    if (!this.selectedDatabase) {
      alert('No database selected.');
      return;
    }

    this.isDiscoveringDatabases = true;

    const payload = {
      url: this.systemUrl,
      databases: [this.selectedDatabase],
      credentials_map: {
        [this.selectedDatabase]: this.dbCredentials
      }
    };

    this.http.post('http://127.0.0.1:8000/reg/extract-data/', payload).subscribe({
      next: (res) => {
        console.log('Data extraction started:', res);
        this.isDiscoveringDatabases = false;
        this.showProgressModal = false;
        this.resetModalState();
        alert('Data extraction initiated successfully.');
      },
      error: (err) => {
        this.isDiscoveringDatabases = false;
        console.error('Data extraction failed:', err);
        alert('Failed to start data extraction.');
      }
    });
  }

  resetModalState(): void {
    this.progressValue = 0;
    this.progressMessage = 'Installing Agent...';
    this.step = 'progress';
    this.dbCredentials = { host: '', port: '', username: '', password: '', extra: '' };
    this.selectedDatabase = null;
    this.isDiscoveringDatabases = false;
  }

  closeModal(): void {
    this.showProgressModal = false;
    this.resetModalState();
  }
}
