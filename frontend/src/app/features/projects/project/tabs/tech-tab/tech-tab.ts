import {ChangeDetectionStrategy, Component, input} from '@angular/core';
import {NgOptimizedImage} from '@angular/common';
import {TechnologyI} from '../../../projects-service';

@Component({
  selector: 'app-tech-tab',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {class: 'flex flex-col flex-1 min-h-0'},
  imports: [NgOptimizedImage],
  templateUrl: './tech-tab.html',
  styleUrl: './tech-tab.css',
})
export class TechTab {
  technologies = input<TechnologyI[]>([]);

  letter(name: string): string {
    return name.charAt(0).toUpperCase();
  }
}
