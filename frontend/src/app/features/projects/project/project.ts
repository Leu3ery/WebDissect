import {Component, output} from '@angular/core';

@Component({
  selector: 'app-project',
  imports: [],
  templateUrl: './project.html',
  styleUrl: './project.css',
})
export class Project {
  openNavLeftOutput = output()

  openNavLeft() {
    this.openNavLeftOutput.emit()
  }
}
