import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ResourceUsageMonitorComponent } from './resource-usage-monitor.component';

describe('ResourceUsageMonitorComponent', () => {
  let component: ResourceUsageMonitorComponent;
  let fixture: ComponentFixture<ResourceUsageMonitorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ResourceUsageMonitorComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ResourceUsageMonitorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
