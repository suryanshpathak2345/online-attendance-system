import apiClient from './client';

export interface PersonalSubjectItem {
  id: number;
  name: string;
  code?: string | null;
  target_percentage: number;
  conducted: number;
  attended: number;
  absent: number;
  percentage: number | null;
  mode: string;
}

export interface PersonalRecordItem {
  id: number;
  personal_subject_id: number;
  subject_name: string;
  record_date: string;
  status: 'PRESENT' | 'ABSENT' | 'HALF_DAY' | 'CANCELLED';
  notes?: string | null;
  mode: string;
}

export const personalApi = {
  getSubjects: async (): Promise<PersonalSubjectItem[]> => {
    const res = await apiClient.get<PersonalSubjectItem[]>('/api/personal/subjects');
    return res.data;
  },
  createSubject: async (name: string, code?: string, targetPercentage = 75.0) => {
    const res = await apiClient.post('/api/personal/subjects', {
      name,
      code,
      target_percentage: targetPercentage,
    });
    return res.data;
  },
  getRecords: async (subjectId?: number): Promise<PersonalRecordItem[]> => {
    const res = await apiClient.get<PersonalRecordItem[]>('/api/personal/records', {
      params: subjectId ? { personal_subject_id: subjectId } : {},
    });
    return res.data;
  },
  saveRecord: async (subjectId: number, recordDate: string, status: string, notes?: string) => {
    const res = await apiClient.post('/api/personal/records', {
      personal_subject_id: subjectId,
      record_date: recordDate,
      status,
      notes,
    });
    return res.data;
  },
  deleteRecord: async (recordId: number) => {
    const res = await apiClient.delete(`/api/personal/records/${recordId}`);
    return res.data;
  },
};
