import apiClient from './client';

export interface ClassRoom {
  id: number;
  name: string;
  section: string;
  academic_year: string;
  description?: string | null;
  is_archived: boolean;
  created_at: string;
  student_count: number;
  subject_count: number;
}

export interface ClassCreatePayload {
  name: string;
  section: string;
  academic_year: string;
  description?: string;
}

export interface ClassUpdatePayload {
  name?: string;
  section?: string;
  academic_year?: string;
  description?: string;
  is_archived?: boolean;
}

export const classesApi = {
  list: async (includeArchived = false): Promise<ClassRoom[]> => {
    const res = await apiClient.get<ClassRoom[]>('/api/classes', {
      params: { include_archived: includeArchived },
    });
    return res.data;
  },
  get: async (id: number): Promise<ClassRoom> => {
    const res = await apiClient.get<ClassRoom>(`/api/classes/${id}`);
    return res.data;
  },
  create: async (payload: ClassCreatePayload): Promise<ClassRoom> => {
    const res = await apiClient.post<ClassRoom>('/api/classes', payload);
    return res.data;
  },
  update: async (id: number, payload: ClassUpdatePayload): Promise<ClassRoom> => {
    const res = await apiClient.patch<ClassRoom>(`/api/classes/${id}`, payload);
    return res.data;
  },
  delete: async (id: number): Promise<{ message: string }> => {
    const res = await apiClient.delete<{ message: string }>(`/api/classes/${id}`);
    return res.data;
  },
};
