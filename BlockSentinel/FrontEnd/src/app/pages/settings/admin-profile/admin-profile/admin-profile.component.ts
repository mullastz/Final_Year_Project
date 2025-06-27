import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { AdminService } from '../../../../services/admin/admin.service';
import { Admin } from '../../../../interface/admin';
import { AdminProfileService } from '../../../../services/admin-profile/admin-profile.service';

@Component({
  selector: 'app-admin-profile',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './admin-profile.component.html',
})
export class AdminProfileComponent implements OnInit {
  constructor(
    private adminService: AdminService,
    private router: Router,
    private adminProfileService: AdminProfileService
  ) {}

  ngOnInit(): void {
    this.loadAdmins();
    this.loadAdminProfile();
  }

  // --- 🔄 Dynamic Admin Profile Logic ---
  admin = {
    name: '',
    email: '',
    photo: ''
  };

  editForm = {
    name: '',
    email: '',
    photo: null as File | string | null,
    photoPreview: ''
  };

  showEditModal = false;

  loadAdminProfile(): void {
    this.adminProfileService.getAdminProfile().subscribe(res => {
      this.admin = {
        name: res.display_name || 'No Name',
        email: res.user?.email || 'No Email',
        photo: res.profile_photo ? `http://localhost:8000${res.profile_photo}` : ''
      };
  
      this.editForm = {
        name: res.display_name || '',
        email: res.user?.email || '',
        photo: res.profile_photo || '',
        photoPreview: res.profile_photo ? `http://localhost:8000${res.profile_photo}` : ''
      };
    });
  }
  

  openEditModal(): void {
    this.showEditModal = true;
  }

  closeEditModal(): void {
    this.showEditModal = false;
  }

  triggerFileInput() {
    const input = document.querySelector<HTMLInputElement>('input[type="file"]');
    input?.click();
  }

  handleImageUpload(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.editForm.photo = file;

      const reader = new FileReader();
      reader.onload = () => {
        this.editForm.photoPreview = reader.result as string;
      };
      reader.readAsDataURL(file);
    }
  }

  submitChanges(): void {
    const formData = new FormData();
    formData.append('name', this.editForm.name);
    formData.append('email', this.editForm.email);

    if (this.editForm.photo && typeof this.editForm.photo !== 'string') {
      formData.append('photo', this.editForm.photo);
    }

    this.adminProfileService.updateAdminProfile(formData).subscribe({
      next: () => {
        this.loadAdminProfile();
        this.closeEditModal();
      },
      error: (err) => {
        console.error('Update failed:', err);
      }
    });
  }

  // --- ➕ Add New Admin Routing ---
  navigateToAddNewAdmin() {
    this.router.navigate(['/dashboard-pages/settings/add-new-admin']);
  }

  // --- 🔐 Security Section Logic ---
  showPasswordModal = false;
  passwordFocus = '';
  passwordMatchStatus: 'empty' | 'match' | 'mismatch' = 'empty';
  passwordForm = { current: '', new: '', confirm: '' };
  passwordVisible = { current: false, new: false, confirm: false };
  passwordStrength: 'weak' | 'medium' | 'strong' | '' = '';
  passwordTips: string[] = [];
  matchTips: string[] = [];

  openPasswordModal() {
    this.showPasswordModal = true;
  }

  closePasswordModal() {
    this.showPasswordModal = false;
    this.passwordForm = { current: '', new: '', confirm: '' };
    this.passwordStrength = '';
    this.passwordTips = [];
    this.matchTips = [];
    this.passwordVisible = { current: false, new: false, confirm: false };
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
    const tips: string[] = [];
    let strength = 0;

    if (password.length >= 8) strength++; else tips.push('Minimum 8 characters');
    if (/[A-Z]/.test(password)) strength++; else tips.push('At least one uppercase letter');
    if (/[a-z]/.test(password)) strength++; else tips.push('At least one lowercase letter');
    if (/\d/.test(password)) strength++; else tips.push('At least one number');
    if (/[^A-Za-z0-9]/.test(password)) strength++; else tips.push('At least one special character');

    this.passwordTips = tips;
    if (strength <= 2) this.passwordStrength = 'weak';
    else if (strength <= 4) this.passwordStrength = 'medium';
    else this.passwordStrength = 'strong';
  }

  submitPasswordChange() {
    if (!this.passwordForm.current) {
      alert('Please enter your current password first.');
      return;
    }
    if (this.passwordForm.new !== this.passwordForm.confirm) {
      alert('New passwords do not match!');
      return;
    }
  
    this.adminProfileService.changeAdminPassword({
      current_password: this.passwordForm.current,
      new_password: this.passwordForm.new,
      confirm_password: this.passwordForm.confirm
    }).subscribe({
      next: (res: any) => {
        alert((res as any).success || 'Password changed.');
        localStorage.clear();
        sessionStorage.clear();
        window.location.href = '/login';
      },
      
      error: (err) => {
        alert(err.error?.error || 'Failed to change password.');
      }
    });
  
    this.closePasswordModal();
  }
  

  // --- 👥 Manage Admin Logic ---
  admins: Admin[] = [];
  dropdownOpen: number | null = null;

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
    console.log('Editing admin:', admin);
  }

  // --- Admin Edit Modal for Roles ---
  showAdminEditModal = false;
  editAdminForm = {
    id: 0,
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

  closeAdminEditModal() {
    this.showAdminEditModal = false;
  }

  submitEditAdmin() {
    if (this.editAdminForm.password && this.editAdminForm.password !== this.editAdminForm.confirmPassword) {
      alert('Passwords do not match');
      return;
    }
  
    const data: any = {
      admin_name: this.editAdminForm.name,
      email: this.editAdminForm.email,
      role: this.editAdminForm.role
    };
  
    if (this.editAdminForm.password) {
      data.password = this.editAdminForm.password;
    }
  
    this.adminService.updateAdmin(this.editAdminForm.id, data).subscribe({
      next: () => {
        alert('Admin updated successfully.');
        this.loadAdmins(); // Refresh
        this.closeAdminEditModal();
      },
      error: (err) => {
        alert('Failed to update admin.');
        console.error(err);
      }
    });
  }
  

  checkEditPasswordStrength() {
    const pwd = this.editAdminForm.password;
    const tips: string[] = [];

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
    // Optional: add visual cue if password matches
  }
}
