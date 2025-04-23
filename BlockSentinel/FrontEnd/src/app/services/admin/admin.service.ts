import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Admin } from '../../interface/admin';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AdminService {
  private apiUrl = 'http://localhost:3009/admins'; // JSON server

  constructor(private http: HttpClient) {}

  getAdmins(): Observable<Admin[]> {
    return this.http.get<Admin[]>(this.apiUrl);
  }

  deleteAdmin(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }

  updateAdmin(id: number, editAdminForm: { id: number; name: string; email: string; role: string; permission: string; password: string; confirmPassword: string; }, admin: Admin): Observable<Admin> {
    return this.http.put<Admin>(`${this.apiUrl}/${admin.id}`, admin);
  }

  addAdmin(admin: Admin): Observable<Admin> {
    return this.http.post<Admin>(this.apiUrl, admin);
  }
}
