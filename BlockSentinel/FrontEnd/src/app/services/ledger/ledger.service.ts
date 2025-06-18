import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class LedgerService {
  constructor(private http: HttpClient) {}

  async getLedgerBySystemAndBatch(systemId: string, tableId: string) {
    const url = `http://localhost:8000/reg/api/system/${systemId}/ledger/${tableId}/`;
    const response = await this.http.get<any>(url).toPromise();

    const data = response.data;  // ✅ Fix: extract 'data' from response

    const columnNames = data.schema.map((col: [string, string]) => col[0]);

    const formattedRows = data.rows.map((row: any[]) => {
      const obj: any = {};
      columnNames.forEach((col: string, index: number) => {
        obj[col] = row[index];
      });
      return obj;
    });

    return {
      batchId: tableId,
      description: data.tableName,
      systemId,
      data: formattedRows,
      columns: columnNames
    };
  }
}
