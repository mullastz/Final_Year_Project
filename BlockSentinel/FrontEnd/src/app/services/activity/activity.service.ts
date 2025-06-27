import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Activity } from '../../interface/activity';
import { map } from 'rxjs/operators';


@Injectable({
  providedIn: 'root'
})
export class ActivityService {
  private apiUrl = 'http://127.0.0.1:8000/auditlog/monitoring/activity/';

  constructor(private http: HttpClient) {}

getActivities(): Observable<Activity[]> {
  return this.http.get<any[]>(this.apiUrl).pipe(
    map((events: any[]) => events.map(event => ({
      timestamp: event.timestamp?.split('T')[0] || '',
      time: event.timestamp?.split('T')[1]?.split('.')[0] || '',
      user: event.user || 'Unknown',
      action: event.event_type,
      affectedData: event.description,
      status: event.system_id // system_id mapped to status column
    })))
  );
}

}
