import apiClient from './client';

export interface LoginPayload {
  email: string;
  password: string;
}

export interface StudentAccessPayload {
  roll_number: string;
  class_id: number;
  secret_passcode?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  email: string;
  full_name: string;
  role: 'admin' | 'teacher' | 'student';
  student_id?: number | null;
  class_id?: number | null;
}

export interface UserProfile {
  id: number;
  email: string;
  full_name: string;
  role: 'admin' | 'teacher' | 'student';
  student_id?: number | null;
  class_id?: number | null;
  assigned_classes: Array<{
    assignment_id: number;
    class_id: number;
    class_name: string;
    class_section: string;
    subject_id: number;
    subject_name: string;
    subject_code: string;
  }>;
}

export const authApi = {
  login: async (payload: LoginPayload): Promise<AuthResponse> => {
    const res = await apiClient.post<AuthResponse>('/api/auth/login', payload);
    return res.data;
  },
  studentAccess: async (payload: StudentAccessPayload): Promise<AuthResponse> => {
    const res = await apiClient.post<AuthResponse>('/api/auth/student-access', payload);
    return res.data;
  },
  getProfile: async (): Promise<UserProfile> => {
    const res = await apiClient.get<UserProfile>('/api/auth/me');
    return res.data;
  },
  logout: async (): Promise<void> => {
    await apiClient.post('/api/auth/logout');
  },
};
