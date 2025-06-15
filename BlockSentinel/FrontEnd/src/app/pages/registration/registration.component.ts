import { Component, OnInit } from '@angular/core';
import { v4 as uuidv4 } from 'uuid'; 
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { RegistrationService } from '../../services/registration/registration.service';
import { Router } from '@angular/router';

type ModalStep = 'progress' | 'selectDb' | 'enterCredentials';
interface DiscoveredDatabase {
  name: string;
  type: string;
}


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
  discoveredDbTypes: DiscoveredDatabase[] = [];
  selectedDatabase: string | null = null;
  selectedDatabases: Set<string> = new Set();
  

  isRegistering = false;
  isInstallingAgent = false;
  isDiscoveringDatabases = false;
  isDatabaseSelectionVisible = false;

  selectedSystemId: string = '';
  selectedDisplayId: string = '';

  selectedDbType: string = '';
  credentials = { host: '', port: '', user: '', password: '' };
  databaseNames: string[] = [];

// UI flags
showCredentialForm = false;
loadingDbNames = false;
errorMessage = '';

securityComplete = false;

  constructor(private http: HttpClient, private registrationService: RegistrationService,
    private router: Router
  ) {}

  ngOnInit(): void {
    const fullId = uuidv4(); // generate UUID
    this.systemId = 'SYS-' + fullId.split('-')[0]; // format to SYS-xxxxxxx

    this.registrationService.securityCompleted$.subscribe(status => {
      this.securityComplete = status;
    });
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

   // Example: after scanning system, set discoveredDbTypes
   onDiscoveredDbTypes(dbName: string[]) {
    this.discoveredDbTypes = dbName.map(dbType => ({ name: dbType, type: dbType }));
  }

  onSelectDbType(dbName: string) {
    this.selectedDbType = dbName;
    this.showCredentialForm = true;
    this.databaseNames = [];
    this.selectedDatabase = null;
    this.errorMessage = '';
    // Reset credentials if needed
    this.credentials = { host: '', port: '', user: '', password: '' };
  }

  fetchDatabases() {
    this.loadingDbNames = true;
    this.errorMessage = '';
  
    const ipAddress = this.systemUrl.split('//')[1].split(':')[0]; // Extract IP from URL
  
    this.registrationService.fetchDatabaseNames(this.selectedDbType, this.credentials, ipAddress)
      .subscribe({
        next: (res) => {
          this.databaseNames = res.database_names || [];
          this.loadingDbNames = false;
          if (!this.databaseNames.length) {
            this.errorMessage = 'No databases found.';
          }
        },
        error: (err) => {
          this.errorMessage = err.error?.error || 'Failed to fetch databases. Check your credentials.';
          this.loadingDbNames = false;
        }
      });
  }
  
  fetchDatabaseNames(): void {
    this.loadingDbNames = true;
    this.errorMessage = '';
    this.databaseNames = [];
  
    const ipAddress = this.systemUrl.split('//')[1].split(':')[0]; // Extract IP from URL
  
    const payload = {
      db_type: this.selectedDbType,
      credentials: {
        host: this.credentials.host,
        port: this.credentials.port,
        user: this.credentials.user,
        password: this.credentials.password,
      },
      ip_address: ipAddress
    };
  
    this.http.post<{ database_names: string[] }>('http://127.0.0.1:8000/reg/get-database-names/', payload).subscribe({
      next: (res) => {
        this.loadingDbNames = false;
        this.databaseNames = res.database_names || [];
  
        if (this.databaseNames.length === 0) {
          this.errorMessage = 'No databases found.';
        }
      },
      error: (err) => {
        this.loadingDbNames = false;
        const detail = err?.error?.error || 'Failed to fetch databases. Check your credentials.';
        this.errorMessage = detail;
        console.error('Fetch DB names failed:', err);
      }
    });
  }
  

  onSelectDatabase(dbName: string) {
    this.selectedDatabase = dbName;
  }

  onDbTypeChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    this.onSelectDbType(target.value);
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

        this.http.get<{ databases: string[] }>(`http://127.0.0.1:8000/reg/discover-databases/?url=${this.systemUrl}`)
          .subscribe({
            next: (res) => {
              this.progressValue = 100;
              this.progressMessage = 'Discovery complete.';
              this.discoveredDbTypes = res.databases.map(type => ({ name: type, type }));
              this.step = 'selectDb';
              this.isDiscoveringDatabases = false;
            },
            error: (err) => {
              this.loadingDbNames = false;
              const detail = err?.error?.error || 'Failed to fetch databases. Check your credentials.';
              this.errorMessage = detail;
              console.error('Fetch DB names failed:', err);
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
    const agentUrl = this.systemUrl; // Replace this with wherever you're storing the system URL
    const dbList = Array.from(this.selectedDatabases).map(name => ({
      name,
      type: this.selectedDbType
    }));
  
    const credentialsMap: any = {};
    this.selectedDatabases.forEach(dbName => {
      credentialsMap[dbName] = {
        host: this.credentials.host,
        port: this.credentials.port,
        user: this.credentials.user,
        password: this.credentials.password,
        database: dbName 
      };
    });
  
    const payload = {
      url: agentUrl,
      db_name: dbList,
      credentials: credentialsMap,
      system_id: this.systemId
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
    this.discoveredDbTypes = response.discovered_databases
  }

  
  submitDbCredentials(): void {
    if (!this.selectedDatabase) {
      alert('No database selected.');
      return;
    }
  
    const dbName = this.selectedDatabase;
    const dbType = this.selectedDbType;
  
    const payload = {
      url: this.systemUrl,
      db_name: [
        {
          name: dbName,
          type: dbType
        }
      ],
      credentials: {
        [dbName]: {
          host: this.credentials.host,
          port: this.credentials.port,
          user: this.credentials.user,
          password: this.credentials.password,
          database: dbName 
        }
      },
      system_id: this.systemId
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

  handleDbSubmission(): void {
    if (this.selectedDatabases.size === 0) {
      alert('Please select at least one database.');
      return;
    }
  
    if (this.selectedDatabases.size === 1) {
      // Extract the only selected db name
      const dbName = Array.from(this.selectedDatabases)[0];
  
      const payload = {
        url: this.systemUrl,
        db_name: [
          {
            name: dbName,
            type: this.selectedDbType
          }
        ],
        credentials: {
          [dbName]: {
            host: this.credentials.host,
            port: this.credentials.port,
            user: this.credentials.user,
            password: this.credentials.password,
            database: dbName 
          }
        },
        system_id: this.systemId
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
  
    } else {
      // Multiple databases, use the existing secureDatabases logic
      this.secureDatabases();
    }
  }
  
  
  goToManagement() {
    this.registrationService.resetSecurityStatus();
    this.router.navigate(['/management']);
  }
 
  resetModalState(): void {
    this.progressValue = 0;
    this.progressMessage = 'Installing Agent...';
    this.step = 'progress';
    this.credentials = { host: '', port: '', user: '', password: ''};
    this.selectedDatabase = null;
    this.isDiscoveringDatabases = false;
  }

  closeModal(): void {
    this.showProgressModal = false;
    this.resetModalState();
  }
}
