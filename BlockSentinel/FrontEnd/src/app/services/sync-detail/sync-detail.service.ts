import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { SyncDetail } from '../../interface/sync-detail';

@Injectable({
  providedIn: 'root'
})
export class SyncDetailService {
  private apiUrl = 'http://localhost:3008/sync-detail';

  constructor(private http: HttpClient) {}

  getSyncDetails(): Observable<SyncDetail[]> {
    return this.http.get<SyncDetail[]>(this.apiUrl);
  }
}
