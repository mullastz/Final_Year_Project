import { Component, OnInit } from '@angular/core';
import { WebhookService } from '../../../../services/webhook/webhook.service';
import { Webhook } from '../../../../interface/webhook';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-advanced-configuration',
  imports: [FormsModule, CommonModule],
  templateUrl: './advanced-configuration.component.html',
  styleUrls: ['./advanced-configuration.component.css']
})
export class AdvancedConfigurationComponent implements OnInit {
  webhooks: Webhook[] = [];
  newWebhook: Webhook = { id: 0, url: '', event: '', status: 'active' };
  isModalOpen = false;
  isEditing = false;
  editingId: number | null = null;
  eventTypes: string[] = ['CREATE', 'UPDATE', 'DELETE', 'SYNC']; // adjust as needed


  constructor(private webhookService: WebhookService) {}

  ngOnInit(): void {
    this.loadWebhooks();
  }

  loadWebhooks(): void {
    this.webhookService.getWebhooks().subscribe(data => this.webhooks = data);
  }

  openModal(): void {
    this.isModalOpen = true;
    this.newWebhook = { id: 0, url: '', event: '', status: 'active' };
    this.isEditing = false;
    this.editingId = null;
  }

  closeModal(): void {
    this.isModalOpen = false;
  }

  saveWebhook(): void {
    if (this.isEditing && this.editingId !== null) {
      this.webhookService.updateWebhook(this.editingId, this.newWebhook).subscribe(() => {
        this.loadWebhooks();
        this.closeModal();
      });
    } else {
      this.webhookService.addWebhook(this.newWebhook).subscribe(() => {
        this.loadWebhooks();
        this.closeModal();
      });
    }
  }

  editWebhook(webhook: Webhook): void {
    this.newWebhook = { ...webhook };
    this.isEditing = true;
    this.editingId = webhook.id;
    this.openModal();
  }

  deleteWebhook(id: number): void {
    this.webhookService.deleteWebhook(id).subscribe(() => {
      this.webhooks = this.webhooks.filter(hook => hook.id !== id);
    });
  }

  testWebhook(id: number): void {
    alert(`Testing webhook with ID: ${id}`);
  }

  toggleActionMenu(webhook: Webhook): void {
    webhook['showMenu'] = !webhook['showMenu'];
  }
  
}
