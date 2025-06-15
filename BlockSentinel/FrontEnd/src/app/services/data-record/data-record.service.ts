import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { DataRecord } from '../../interface/data-record';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class DataRecordService {
  constructor(private http: HttpClient) {}

  getDataRecords(sysId: string): Observable<DataRecord[]> {
    return this.http.get<any>(`http://localhost:8000/reg/api/system/${sysId}/ledger/summary/`).pipe(
      map(response => (response.data || []).map((item: any) => ({
        batchId: item.table_id,
        description: item.description,
        total: item.total_rows,
        date: new Date(item.timestamp).toLocaleDateString(),
        time: new Date(item.timestamp).toLocaleTimeString(),
        ledgerHash: item.ledger_hash
      })))
    );
  }
  
  
  
}
