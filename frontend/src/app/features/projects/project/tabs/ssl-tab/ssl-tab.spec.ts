import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SslTab } from './ssl-tab';

describe('SslTab', () => {
  let component: SslTab;
  let fixture: ComponentFixture<SslTab>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SslTab]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SslTab);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
