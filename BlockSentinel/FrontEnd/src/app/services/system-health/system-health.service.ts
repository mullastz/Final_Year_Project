import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { SystemHealth } from '../../interface/system-health';

@Injectable({
  providedIn: 'root'
})
export class SystemHealthService {
  private apiUrl = 'http://localhost:8000/auditlog/system-health/';

  constructor(private http: HttpClient) {}

  getSystemHealth(): Observable<SystemHealth[]> {
    return this.http.get<SystemHealth[]>(this.apiUrl);
  }

  retryService(service: string): Observable<any> {
    return this.http.post('http://localhost:8000/auditlog/system-health/retry/', { service });
  }
  
  getServiceLogs(service: string): Observable<{ logs: string[] }> {
    return this.http.get<{ logs: string[] }>(`${this.apiUrl}/logs/${service}`);
  }
  
  stopAgent(): Observable<any> {
    return this.http.post(`${this.apiUrl}/stop-agent/`, {});
  }
  
}
