import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-data-export-backup-logs',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './data-backup.component.html',
  styleUrls: ['./data-backup.component.css']
})
export class DataBackupComponent {

  exportForm = {
    system: '',
    grouping: '',
    format: '',
    exportNow: '',
    auto: '',
    exportFrequency: '',
    destination: ''
  };

  // Backup Schedule Model
  backupSchedule = {
    frequency: '',
    time: '',
    location: ''
  };

  // Log Settings Model
  logSettings = {
    retain: '',
    download: '',
    smartFilter: false,
    autoExport: ''
  };

  // EXPORT LEDGER DATA DROPDOWNS
  systemsOptions = ['System A', 'System B', 'System C'];
  groupingStyleOptions = ['By Date', 'By Type', 'By User'];
  formatsOptions = ['CSV', 'PDF', 'XLSX'];
  exportNowOptions = ['Current Data', 'Last 7 Days', 'Last 30 Days'];
  autoExportOptions = ['Enabled', 'Disabled'];
  exportFrequencyOptions = ['Daily', 'Weekly', 'Monthly'];
  exportDestinationOptions = ['Email', 'Cloud Storage', 'Local Disk'];

  selectedSystem = this.systemsOptions[0];
  selectedGroupingStyle = this.groupingStyleOptions[0];
  selectedFormat = this.formatsOptions[0];
  selectedExportNow = this.exportNowOptions[0];
  selectedAutoExport = this.autoExportOptions[0];
  selectedExportFrequency = this.exportFrequencyOptions[0];
  selectedExportDestination = this.exportDestinationOptions[0];

  // BACKUP & RECOVERY
  backupFrequencyOptions = ['Daily', 'Weekly', 'Monthly'];
  backupTimeOptions = ['12:00 AM', '6:00 AM', '12:00 PM', '6:00 PM'];
  backupLocationOptions = ['Cloud Storage', 'Local Disk', 'External Drive'];

  selectedBackupFrequency = this.backupFrequencyOptions[0];
  selectedBackupTime = this.backupTimeOptions[0];
  selectedBackupLocation = this.backupLocationOptions[0];

  // ACTIVITY LOGS SETTINGS
  retainLogsOptions = ['1 Week', '1 Month', '3 Months', '6 Months', '1 Year'];
  downloadLogsOptions = ['CSV', 'PDF', 'JSON'];
  autoExportLogsOptions = ['Enabled', 'Disabled', 'On Schedule'];

  selectedRetainLogs = this.retainLogsOptions[0];
  selectedDownloadLogs = this.downloadLogsOptions[0];
  selectedAutoExportLogs = this.autoExportLogsOptions[0];

  smartLogFiltersEnabled = false;

  // BUTTON HANDLERS
  generateLedgerBackup() {
    console.log(' Generating Ledger Backup...');
    console.log({
      system: this.selectedSystem,
      grouping: this.selectedGroupingStyle,
      format: this.selectedFormat,
      exportTime: this.selectedExportNow,
      autoExport: this.selectedAutoExport,
      frequency: this.selectedExportFrequency,
      destination: this.selectedExportDestination
    });
    // TODO: Connect to backend export API
  }

  restoreBackup() {
    console.log(' Restore Backup triggered');
    console.log({
      frequency: this.selectedBackupFrequency,
      time: this.selectedBackupTime,
      location: this.selectedBackupLocation
    });
    // TODO: Connect to backend restore logic
  }

  toggleSmartLogFilters() {
    this.smartLogFiltersEnabled = !this.smartLogFiltersEnabled;
    console.log(' Smart Log Filters toggled:', this.smartLogFiltersEnabled);
    // TODO: Trigger UI change / filtering logic
  }
}
