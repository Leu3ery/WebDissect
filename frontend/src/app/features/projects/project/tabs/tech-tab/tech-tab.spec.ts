import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TechTab } from './tech-tab';

describe('TechTab', () => {
  let component: TechTab;
  let fixture: ComponentFixture<TechTab>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TechTab]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TechTab);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
