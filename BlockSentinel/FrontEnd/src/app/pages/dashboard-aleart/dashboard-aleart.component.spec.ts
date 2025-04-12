import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DashboardAleartComponent } from './dashboard-aleart.component';

describe('DashboardAleartComponent', () => {
  let component: DashboardAleartComponent;
  let fixture: ComponentFixture<DashboardAleartComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardAleartComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DashboardAleartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
