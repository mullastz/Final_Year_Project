import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SystemHealthOverviewComponent } from './system-health-overview.component';

describe('SystemHealthOverviewComponent', () => {
  let component: SystemHealthOverviewComponent;
  let fixture: ComponentFixture<SystemHealthOverviewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SystemHealthOverviewComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SystemHealthOverviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
