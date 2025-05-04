import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { RegisteredSystem } from '../../interface/registered-system';

@Injectable({
  providedIn: 'root'
})
export class SystemService {
  private apiUrl = 'http://127.0.0.1:8000/reg/list-systems';

  constructor(private http: HttpClient) {}

  getRegisteredSystems(): Observable<RegisteredSystem[]> {
    return this.http.get<any[]>(this.apiUrl).pipe(
      map((data) =>
        data.map((item) => ({
          id: item.display_id || item.system_id,
          name: item.name,
          logoUrl: item.profile_photo || 'assets/images/default.png',
          url: item.system_url,
          type: item.system_type,
          dataType: item.data_type,
          status: item.status || 'active', // or derive from health, etc.
          alert: item.alert_message || 'None',
          health: item.health_status || 'Good',
          admins: item.admins || []
        }))
      )
    );
  }
  

  getSystemById(displayId: string): Observable<RegisteredSystem> {
    return this.http.get<any>(`http://127.0.0.1:8000/reg/get-system/${displayId}/`).pipe(
      map((item) => ({
        id: item.display_id || item.system_id,
        name: item.name,
        logoUrl:  `http://127.0.0.1:8000${item.profile_photo}` || 'assets/images/default.png',
        url: item.url,
        type: item.system_type,
        dataType: item.data_type,
        status: item.status || 'active',
        alert: item.alert_message || 'None',
        health: item.health_status || 'Good',
        admins: item.admins || []
      }))
    );
  }
}
  

