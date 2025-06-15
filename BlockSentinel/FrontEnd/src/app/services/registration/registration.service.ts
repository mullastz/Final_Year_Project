// src/app/services/registration.service.ts
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class RegistrationService {
  private securityCompleted = new BehaviorSubject<boolean>(false);
  securityCompleted$ = this.securityCompleted.asObservable();

  installAgent(systemUrl: string) {
    throw new Error('Method not implemented.');
  }
  private baseUrl = 'http://localhost:8000/reg'; // Adjust as needed

  constructor(private http: HttpClient) {}

  registerSystem(data: FormData) {
    return this.http.post(`${this.baseUrl}/register-system/`, data);
  }

  fetchDatabaseNames(dbType: string, credentials: any, ipAddress: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/get-database-names/`, {
      db_type: dbType,
      credentials: credentials,
      ip_address: ipAddress
    });
  }  

  getDatabaseNames(payload: any): Observable<string[]> {
    return this.http.post<string[]>('http://127.0.0.1:8000/reg/fetch-database-names/', payload);
  }
  
  extractData(data: any) {
    return this.http.post(`${this.baseUrl}/extract-data/`, data);
  }

  markSecurityComplete() {
    this.securityCompleted.next(true);
  }

  resetSecurityStatus() {
    this.securityCompleted.next(false);
  }
}
