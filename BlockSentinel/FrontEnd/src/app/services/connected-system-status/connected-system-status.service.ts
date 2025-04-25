import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ConnectedSystemStatus } from '../../interface/connected-system-status';


@Injectable({
  providedIn: 'root'
})
export class ConnectedSystemStatusService {
  private dataUrl = 'http://localhost:3014/connected-system';

  constructor(private http: HttpClient) {}

  getConnectedSystems(): Observable<ConnectedSystemStatus[]> {
    return this.http.get<ConnectedSystemStatus[]>(this.dataUrl);
  }
}
