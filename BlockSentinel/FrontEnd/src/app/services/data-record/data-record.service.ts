import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DataRecord } from '../../interface/data-record';

@Injectable({
  providedIn: 'root'
})
export class DataRecordService {
  private jsonURL = 'http://localhost:3004/data-record';

  constructor(private http: HttpClient) {}

  getDataRecords(): Observable<DataRecord[]> {
    return this.http.get<DataRecord[]>(this.jsonURL);
  }
}
