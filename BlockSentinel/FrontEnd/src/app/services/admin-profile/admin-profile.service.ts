import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AdminProfileService {
  private baseUrl = 'http://localhost:8000/settings/admin/profile/';

  constructor(private http: HttpClient) {}

  getAdminProfile(): Observable<any> {
    return this.http.get(this.baseUrl);
  }

  updateAdminProfile(formData: FormData): Observable<any> {
    return this.http.put(this.baseUrl + 'update/', formData);
  }

  changeAdminPassword(data: {
    current_password: string;
    new_password: string;
    confirm_password: string;
  }) {
    return this.http.post('http://localhost:8000/settings/admin/change-password/', data);
  }
  
}
