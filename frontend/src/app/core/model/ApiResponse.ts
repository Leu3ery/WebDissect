export interface ApiResponse<T> {
  data: T;
  // Backend serializes the error under `errorMessage`; `message` is kept for
  // the few mocked flows that still set it.
  errorMessage?: string;
  message?: string;
  isSuccess: boolean;
}
