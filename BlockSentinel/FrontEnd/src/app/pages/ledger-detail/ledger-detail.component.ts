import { Component, OnInit } from '@angular/core';
import { Ledger } from '../../interface/ledger';
import { ActivatedRoute } from '@angular/router';
import { LedgerService } from '../../services/ledger/ledger.service';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';


@Component({
  selector: 'app-ledger-detail',
  imports: [CommonModule, RouterModule],
  templateUrl: './ledger-detail.component.html',
  styleUrls: ['./ledger-detail.component.css']
})
export class LedgerDetailComponent implements OnInit {
  ledger!: Ledger;
  showDownloadDropdown = false;

  constructor(private route: ActivatedRoute, private ledgerService: LedgerService) {}

  ngOnInit(): void {
    const systemId = this.route.snapshot.paramMap.get('systemId')!;
    const batchId = this.route.snapshot.paramMap.get('batchId')!;
    this.ledgerService.getLedgerBySystemAndBatch(systemId, batchId).subscribe(data => {
      if (data) this.ledger = data;
    });
  }

  toggleDownloadDropdown() {
    this.showDownloadDropdown = !this.showDownloadDropdown;
  }
}
