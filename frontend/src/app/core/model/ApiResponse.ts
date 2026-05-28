export interface ApiResponse<T> {
  data: T;
  message: string;
  isSuccess: boolean;
}
