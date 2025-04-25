import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { SystemHealth } from '../../interface/system-health';

@Injectable({
  providedIn: 'root'
})
export class SystemHealthService {
  private apiUrl = 'http://localhost:3012/system-health';

  constructor(private http: HttpClient) {}

  getSystemHealth(): Observable<SystemHealth[]> {
    return this.http.get<SystemHealth[]>(this.apiUrl);
  }
}
