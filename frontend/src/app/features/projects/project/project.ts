import {Component, input, output} from '@angular/core';

@Component({
  selector: 'app-project',
  imports: [],
  templateUrl: './project.html',
  styleUrl: './project.css',
})
export class Project {
  projectId = input()
  openNavLeftOutput = output()

  openNavLeft() {
    this.openNavLeftOutput.emit()
  }
}
