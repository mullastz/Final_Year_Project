import { TestBed } from '@angular/core/testing';

import { AlertNotificationService } from './alert-notification.service';

describe('AlertNotificationService', () => {
  let service: AlertNotificationService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AlertNotificationService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
