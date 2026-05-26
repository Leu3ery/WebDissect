import {Component, output} from '@angular/core';

@Component({
  selector: 'app-nav-left',
  imports: [],
  templateUrl: './nav-left.html',
  styleUrl: './nav-left.css',
})
export class NavLeft {
  closeNavLeftOutput = output()

  closeNavLeft() {
    this.closeNavLeftOutput.emit()
  }
}
