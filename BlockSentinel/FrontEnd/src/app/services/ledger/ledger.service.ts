import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';



@Injectable({ providedIn: 'root' })
export class LedgerService {
  constructor(private http: HttpClient) {}

  async getLedgerBySystemAndBatch(systemId: string, tableId: string) {
    const url = `http://localhost:8000/api/system/${systemId}/ledger/${tableId}/`;
    const data = await this.http.get<any>(url).toPromise();

    return {
      batchId: tableId,
      description: data.table_name,
      systemId,
      data: data.rows,
      columns: data.columns
    };
  }
}
