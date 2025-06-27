import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Alert } from '../../interface/alert';
import { map } from 'rxjs/operators';



@Injectable({
  providedIn: 'root'
})
export class AlertService {
  private apiUrl = 'http://localhost:8000/auditlog/anomalies/';


  constructor(private http: HttpClient) {}

  getAlerts(): Observable<Alert[]> {
    return this.http.get<any[]>(this.apiUrl).pipe(
      map((data) => data.map(item => {
        const [date, time] = item.timestamp.split('T');
        return {
          id: item.id,
          severity: this.mapSeverity(item.severity),
          message: item.description,
          date,
          time: time?.split('.')[0] || '',
          systemId: item.system_id,
          user: item.user || 'N/A',
          eventType: item.event_type || 'N/A',
          source: item.source || 'N/A',
          metadata: item.metadata || {},
        } as Alert;
      }))
    );
  }
  
  
  private mapSeverity(severity: string): 'Critical' | 'Warning' | 'Info' {
    const map: Record<string, 'Critical' | 'Warning' | 'Info'> = {
      'CRITICAL': 'Critical',
      'WARNING': 'Warning',
      'INFO': 'Info',
      'HIGH': 'Critical',
      'MEDIUM': 'Warning',
      'LOW': 'Info'
    };
    return map[severity.toUpperCase()] || 'Info';
  }
  
  
}
