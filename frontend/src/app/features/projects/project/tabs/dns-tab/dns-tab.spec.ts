import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DnsTab } from './dns-tab';

describe('DnsTab', () => {
  let component: DnsTab;
  let fixture: ComponentFixture<DnsTab>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DnsTab]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DnsTab);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
