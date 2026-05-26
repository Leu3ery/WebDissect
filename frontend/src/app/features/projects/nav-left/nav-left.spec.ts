import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NavLeft } from './nav-left';

describe('NavLeft', () => {
  let component: NavLeft;
  let fixture: ComponentFixture<NavLeft>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NavLeft]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NavLeft);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
