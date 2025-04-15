import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-otp-verification',
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './otp-verification.component.html'
})
export class OtpVerificationComponent {
  otpCode: string = '';
  expectedOtp: string = '123456'; // Replace with backend value in real scenario
  errorMessage: string = '';

  constructor(private router: Router) {}

  verifyOtp() {
    if (this.otpCode === this.expectedOtp) {
      // Navigate to dashboard if OTP is correct
      this.router.navigate(['/dashboard']);
    } else {
      this.errorMessage = 'Invalid OTP. Please try again.';
    }
  }

  resendOtp() {
    // In real case: call service to send new OTP
    alert('A new OTP has been sent to your email.');
  }
}
