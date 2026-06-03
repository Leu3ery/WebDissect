import {Component, signal} from '@angular/core';
import {LucideKey, LucideUpload} from '@lucide/angular';
import {DecimalPipe} from '@angular/common';

@Component({
  selector: 'app-new-project',
  imports: [
    LucideKey,
    LucideUpload,
    DecimalPipe,
  ],
  templateUrl: './new-project.html',
  styleUrl: './new-project.css',
})
export class NewProject {
  selectedFile = signal<null | File>(null)

  onFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.item(0)
    if (file) {
      this.selectedFile.set(file);
    }
  }

  getFileSize() {
    return this.selectedFile() != null ? this.selectedFile()!.size / 1000 / 1000 : 0
  }

  getFileName() {
    return this.selectedFile() != null ? this.selectedFile()!.name : 'no file';
  }
}
