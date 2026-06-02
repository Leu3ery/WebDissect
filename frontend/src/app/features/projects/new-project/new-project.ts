import { Component } from '@angular/core';
import {LucideKey, LucideUpload} from '@lucide/angular';

@Component({
  selector: 'app-new-project',
  imports: [
    LucideKey,
    LucideUpload
  ],
  templateUrl: './new-project.html',
  styleUrl: './new-project.css',
})
export class NewProject {

}
