import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EndpointsTab } from './endpoints-tab';

describe('EndpointsTab', () => {
  let component: EndpointsTab;
  let fixture: ComponentFixture<EndpointsTab>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EndpointsTab]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EndpointsTab);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
