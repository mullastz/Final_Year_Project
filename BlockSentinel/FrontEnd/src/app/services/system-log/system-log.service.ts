import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { SystemLog } from '../../interface/system-log'; 

@Injectable({
  providedIn: 'root'
})
export class LogService {
  private apiUrl = 'http://localhost:3006/system-log'; // assuming endpoint name is 'logs'

  constructor(private http: HttpClient) {}

  getLogs(): Observable<SystemLog[]> {
    return this.http.get<SystemLog[]>(this.apiUrl);
  }
}
