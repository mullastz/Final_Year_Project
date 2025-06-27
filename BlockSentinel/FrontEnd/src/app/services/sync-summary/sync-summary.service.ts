// sync-status.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { SyncSummary } from '../../interface/sync-summary';

@Injectable({
  providedIn: 'root'
})
export class SyncStatusService {
  private apiUrl = 'http://127.0.0.1:8000/reg/sync/status/';

  constructor(private http: HttpClient) {}

  getSyncSummary(): Observable<SyncSummary> {
    return this.http.get<SyncSummary>(this.apiUrl);
  }
}
