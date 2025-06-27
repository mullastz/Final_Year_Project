import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-add-new-admin',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './add-new-admin.component.html',
  styleUrls: ['./add-new-admin.component.css']
})
export class AddNewAdminComponent {
  // Form fields
  adminName = '';
  adminEmail = '';
  selectedRole = '';

  // Password form fields and state
  showPasswordModal = false;
  passwordForm = {
    new: '',
    confirm: ''
  };
  passwordVisible = {
    new: false,
    confirm: false
  };
  passwordStrength: 'weak' | 'medium' | 'strong' | '' = '';
  passwordTips: string[] = [];
  matchTips: string[] = [];

  constructor(private http: HttpClient, public router: Router) {}

  // Password Modal
  openPasswordModal() {
    this.showPasswordModal = true;
  }

  closePasswordModal() {
    this.showPasswordModal = false;
    this.passwordForm = { new: '', confirm: '' };
    this.passwordStrength = '';
    this.passwordTips = [];
    this.matchTips = [];
    this.passwordVisible = {
      new: false,
      confirm: false
    };
  }

  // Password visibility toggle
  togglePasswordVisibility(field: 'new' | 'confirm') {
    this.passwordVisible[field] = !this.passwordVisible[field];
  }

  // Called on password input changes
  onNewPasswordChange() {
    this.checkPasswordStrength();
    this.checkPasswordsMatch();
  }

  onConfirmPasswordChange() {
    this.checkPasswordsMatch();
  }

  checkPasswordsMatch() {
    const { new: newPassword, confirm: confirmPassword } = this.passwordForm;

    if (!newPassword || !confirmPassword) {
      this.matchTips = [];
    } else if (newPassword === confirmPassword) {
      this.matchTips = ['✔ Passwords match.'];
    } else {
      this.matchTips = ['✖ Passwords do not match.'];
    }
  }

  checkPasswordStrength() {
    const password = this.passwordForm.new;
    let strength = 0;
    const tips: string[] = [];

    if (password.length >= 8) strength++; else tips.push('Minimum 8 characters');
    if (/[A-Z]/.test(password)) strength++; else tips.push('At least one uppercase letter');
    if (/[a-z]/.test(password)) strength++; else tips.push('At least one lowercase letter');
    if (/\d/.test(password)) strength++; else tips.push('At least one number');
    if (/[^A-Za-z0-9]/.test(password)) strength++; else tips.push('At least one special character');

    this.passwordTips = tips;

    if (strength <= 2) {
      this.passwordStrength = 'weak';
    } else if (strength <= 4) {
      this.passwordStrength = 'medium';
    } else {
      this.passwordStrength = 'strong';
    }
  }

  // 🔐 Final Create Button
  submitNewAdmin() {
    if (
      !this.adminName ||
      !this.adminEmail ||
      !this.selectedRole ||
      !this.passwordForm.new ||
      this.passwordForm.new !== this.passwordForm.confirm
    ) {
      alert('Please complete all fields and make sure passwords match.');
      return;
    }
  
    const newAdmin = {
      name: this.adminName,
      email: this.adminEmail,
      role: this.selectedRole,
      password: this.passwordForm.new
    };
  
    const csrfToken = localStorage.getItem('csrfToken');
  
    this.http.post(
      'http://127.0.0.1:8000/settings/admin/create/',
      newAdmin,
      {
        headers: {
          'X-CSRFToken': localStorage.getItem('csrfToken') || ''
        },
        withCredentials: true
      }
    )
    .subscribe({
      next: () => {
        alert('Admin created successfully.');
        this.router.navigate(['/dashboard-pages/settings/admin-profile']);
      },
      error: (err) => {
        console.error('Failed to create admin:', err);
        alert('Failed to create admin. Check console for details.');
      }
    });
  }
  

  ngOnInit(): void {
    this.fetchCsrfToken();
  }
  
  

  getCookie(name: string): string | null {
    const ca: Array<string> = document.cookie.split(';');
    const cookieName = `${name}=`;
    for (let c of ca) {
      c = c.trim();
      if (c.indexOf(cookieName) === 0) {
        return c.substring(cookieName.length, c.length);
      }
    }
    return null;
  }

  fetchCsrfToken(): void {
    this.http.get<any>('http://127.0.0.1:8000/settings/settings/csrf-token/', {
      withCredentials: true
    }).subscribe({
      next: (res) => {
        localStorage.setItem('csrfToken', res.csrfToken);
        console.log('CSRF token fetched:', res.csrfToken);
      },
      error: (err) => {
        console.error('Failed to fetch CSRF token:', err);
      }
    });
  }
  
  
}
