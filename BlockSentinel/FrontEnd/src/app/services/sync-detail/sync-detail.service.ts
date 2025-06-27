import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { SyncDetail } from '../../interface/sync-detail';

@Injectable({
  providedIn: 'root'
})
export class SyncDetailService {
  private apiUrl = 'http://127.0.0.1:8000/reg/sync-detail/';

  constructor(private http: HttpClient) {}

  getSyncDetails(): Observable<SyncDetail[]> {
    return this.http.get<SyncDetail[]>(this.apiUrl);
  }
}
