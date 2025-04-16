// sync-status.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { SyncSummary } from '../../interface/sync-summary';

@Injectable({
  providedIn: 'root'
})
export class SyncStatusService {
  private apiUrl = 'http://localhost:3007/sync-summary';

  constructor(private http: HttpClient) {}

  getSyncSummary(): Observable<SyncSummary> {
    return this.http.get<SyncSummary>(this.apiUrl);
  }
}
