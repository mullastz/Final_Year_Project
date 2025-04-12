import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DashboardActivityComponent } from './dashboard-activity.component';

describe('DashboardActivityComponent', () => {
  let component: DashboardActivityComponent;
  let fixture: ComponentFixture<DashboardActivityComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardActivityComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DashboardActivityComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
