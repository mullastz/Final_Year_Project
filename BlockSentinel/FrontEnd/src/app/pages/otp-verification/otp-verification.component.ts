import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-otp-verification',
  imports: [CommonModule, FormsModule],
  templateUrl: './otp-verification.component.html',
  styleUrls: ['./otp-verification.component.css'],
})
export class OtpVerificationComponent {
  otpCode: string = '';
  email: string = localStorage.getItem('pendingEmail') || '';
  errorMessage: string = '';
  otpResendTimeout: boolean = false;

  constructor(private http: HttpClient, private router: Router) {}

  // Function to handle OTP verification
  verifyOtp(): void {
    if (!this.otpCode) {
      this.errorMessage = 'Please enter the OTP code.';
      return;
    }
  
    this.http.post<any>('http://127.0.0.1:8000/auth/verify/', {
      email: this.email,
      code: this.otpCode
    }).subscribe(
      (response) => {
        if (response.redirect) {
          //Store the tokens in localStorage
          localStorage.setItem('access_token', response.access);
          localStorage.setItem('refresh_token', response.refresh);
  
          this.router.navigate(['/dashboard']);
        } else {
          this.errorMessage = 'Invalid OTP code. Please try again.';
        }
      },
      (error) => {
        this.errorMessage = error.error?.error || 'Verification failed. Please try again.';
      }
    );
  }
  

  // Function to handle OTP resend
  resendOtp(): void {
    if (this.otpResendTimeout) {
      this.errorMessage = 'Please wait before requesting another OTP.';
      return;
    }

    this.http.post<any>('http://127.0.0.1:8000/auth/resend-code/', {
      email: this.email
    }).subscribe(
      (response) => {
        this.errorMessage = ''; // Reset error message
        this.otpResendTimeout = true; // Set timeout to prevent spamming
        setTimeout(() => {
          this.otpResendTimeout = false; // Allow resend after 60 seconds
        }, 60000); // 1 minute timeout

        // Inform user that OTP was resent
        alert('OTP has been resent. Please check your email.');
      },
      (error) => {
        this.errorMessage = error.error?.error || 'Failed to resend OTP. Please try again.';
      }
    );
  }
}
