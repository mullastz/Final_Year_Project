import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { AdminService } from '../../../../services/admin/admin.service';
import { Admin } from '../../../../interface/admin';
import { Router } from '@angular/router';

@Component({
  selector: 'app-admin-profile',
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './admin-profile.component.html',
})
export class AdminProfileComponent {

navigateToAddNewAdmin() {
  this.router.navigate(['/dashboard-pages/settings/add-new-admin']);
}
  admin = {
    name: 'John Doe',
    email: 'john@example.com',
    photo: '',
  };

  editForm = {
    name: '',
    email: '',
    photo: ''
  };

  showEditModal = false;
  http: any;
  passwordsMatch: boolean | undefined;
  showPassword: boolean | undefined;
  showConfirmPassword: boolean | undefined;

  openEditModal() {
    this.editForm = { ...this.admin };
    this.showEditModal = true;
  }

  closeEditModal() {
    this.showEditModal = false;
  }

  triggerFileInput() {
    const input = document.querySelector<HTMLInputElement>('input[type="file"]');
    input?.click();
  }

  handleImageUpload(event: any) {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        this.editForm.photo = reader.result as string;
      };
      reader.readAsDataURL(file);
    }
  }

  submitChanges() {
    this.admin = { ...this.editForm };
    this.closeEditModal();

    // TODO: Send updated data to backend
    console.log('Updated Admin Info:', this.admin);
  }

  // ----------- Security Section Logic ------------

  showPasswordModal = false;
  passwordFocus: string = '';
  passwordMatchStatus: 'empty' | 'match' | 'mismatch' = 'empty';


  passwordForm = {
    current: '',
    new: '',
    confirm: ''
  };

  passwordVisible = {
    current: false,
    new: false,
    confirm: false
  };

  passwordStrength: 'weak' | 'medium' | 'strong' | '' = '';
  passwordTips: string[] = [];

  openPasswordModal() {
    this.showPasswordModal = true;
  }

  closePasswordModal() {
    this.showPasswordModal = false;
    this.passwordForm = { current: '', new: '', confirm: '' };
    this.passwordStrength = '';
    this.passwordTips = [];
    this.passwordFocus = '';
    this.passwordVisible = {
      current: false,
      new: false,
      confirm: false
    };
  }

  togglePasswordVisibility(field: 'current' | 'new' | 'confirm') {
    this.passwordVisible[field] = !this.passwordVisible[field];
  }

  onNewPasswordChange() {
    this.checkPasswordStrength();
    this.checkPasswordsMatch();
  }
  
  onConfirmPasswordChange() {
    this.checkPasswordsMatch();
  }

  matchTips: string[] = [];

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
  
  submitPasswordChange() {
    if (!this.passwordForm.current) {
      alert('Please enter your current password first.');
      return;
    }

    if (this.passwordForm.new !== this.passwordForm.confirm) {
      alert('Passwords do not match!');
      return;
    }

    if (this.passwordForm.new == this.passwordForm.confirm) {
      alert('Passwords match');
      return;
    }
    

    // Send passwordForm to your backend here
    console.log('Password change submitted', this.passwordForm);

    this.closePasswordModal();
  }

  admins: Admin[] = [];
  dropdownOpen: number | null = null;

  constructor(private adminService: AdminService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadAdmins();
  }

  loadAdmins() {
    this.adminService.getAdmins().subscribe(data => {
      this.admins = data;
    });
  }

  toggleDropdown(id: number) {
    this.dropdownOpen = this.dropdownOpen === id ? null : id;
  }

  deleteAdmin(id: number) {
    this.adminService.deleteAdmin(id).subscribe(() => {
      this.admins = this.admins.filter(admin => admin.id !== id);
    });
  }

  editAdmin(admin: Admin) {
    // Open your role modal here (next step)
    console.log('Editing admin:', admin);
  }

  showAdminEditModal = false;
editAdminForm = {
  id: 0, // Added id property
  name: '',
  email: '',
  role: '',
  permission: '',
  password: '',
  confirmPassword: ''
};

editPasswordVisible = false;
editConfirmVisible = false;
editPasswordStrength = '';
editPasswordTips: string[] = [];

openAdminEditModal(admin: any) {
  this.editAdminForm = { ...admin, confirmPassword: '' };
  this.showAdminEditModal = true;
}

// Renamed to avoid duplication
openAdminEditModalWithData(admin: any) {
  this.editAdminForm = {
    id: admin.id,
    name: admin.name,
    email: admin.email,
    role: admin.role,
    permission: admin.permissions,
    password: '',
    confirmPassword: ''
  };

  this.passwordStrength = '';
  this.passwordStrength = '';
  this.passwordsMatch = true;
  this.showPassword = false;
  this.showConfirmPassword = false;

  this.showEditModal = true;
}


closeAdminEditModal() {
  this.showAdminEditModal = false;
}

submitEditAdmin() {
  if (this.editAdminForm.password !== this.editAdminForm.confirmPassword) {
    alert('Passwords do not match');
    return;
  }

  // Update the admin via JSON server
  this.http.put(`http://localhost:3009/admins/${this.editAdminForm.id}`, this.editAdminForm).subscribe(() => {
    this.loadAdmins(); // refetch from backend
    this.closeAdminEditModal();
  });
}

checkEditPasswordStrength() {
  const pwd = this.editAdminForm.password;
  this.editPasswordTips = [];
  const tips = [];

  if (pwd.length < 8) tips.push('Minimum 8 characters');
  if (!/[A-Z]/.test(pwd)) tips.push('At least one uppercase letter');
  if (!/[a-z]/.test(pwd)) tips.push('At least one lowercase letter');
  if (!/[0-9]/.test(pwd)) tips.push('At least one number');
  if (!/[^A-Za-z0-9]/.test(pwd)) tips.push('At least one special character');

  this.editPasswordTips = tips;

  if (tips.length === 0) this.editPasswordStrength = 'strong';
  else if (tips.length <= 2) this.editPasswordStrength = 'medium';
  else this.editPasswordStrength = 'weak';
}

checkEditPasswordMatch() {
  // Optional: visual cue if password matches
}

}

