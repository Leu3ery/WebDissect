import {ChangeDetectionStrategy, Component, input} from '@angular/core';
import {PortI} from '../../../projects-service';

@Component({
  selector: 'app-ports-tab',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {class: 'flex flex-col flex-1 min-h-0'},
  templateUrl: './ports-tab.html',
})
export class PortsTab {
  ports = input<PortI[]>([]);
}
