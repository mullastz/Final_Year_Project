import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login-page',
  imports: [CommonModule, FormsModule],
  templateUrl: './login-page.component.html',
  styleUrls: ['./login-page.component.css'],
})
export class LoginPageComponent {
  email: string = '';
  password: string = '';
  failedAttempts: number = 0;
  errorMessage: string = '';

  constructor(private http: HttpClient, private router: Router) {}

  login(): void {
    if (!this.email || !this.password) {
      this.errorMessage = 'Email and password are required.';
      return;
    }

    this.http.post<any>('http://127.0.0.1:8000/auth/login/', {
      email: this.email,
      password: this.password
    }).subscribe(
      (response) => {
        if (response.redirect) {
          // Unverified account, redirect to verification
          localStorage.setItem('pendingEmail', response.email);
          this.router.navigate(['/otp-verification']);
        } else {
          // User is verified and received a code in email
          localStorage.setItem('pendingEmail', this.email);
          this.router.navigate(['/otp-verification']);
        }
      },
      (error) => {
        this.errorMessage = error.error?.error || 'Login failed. Please try again.';
      }
    );

    if (this.failedAttempts >= 5) {
      this.errorMessage = 'Too many failed attempts. Try again later.';
      return;
    }

    // simulate sending login request to backend
    // TODO: Replace with actual auth service call
    const isSuccess = false; // mock failure

    if (isSuccess) {
      // Redirect to admin dashboard
    } else {
      this.failedAttempts++;
      this.errorMessage = 'Invalid credentials. Please try again.';
    }
  }
}
