import apiClient from './client';

export interface HolidayItem {
  id: number;
  name: string;
  holiday_date: string;
  holiday_type: 'INSTITUTIONAL' | 'WEEKLY';
  description?: string | null;
  created_at: string;
}

export interface HolidayCreatePayload {
  name: string;
  holiday_date: string;
  holiday_type?: string;
  description?: string;
}

export const holidaysApi = {
  list: async (startDate?: string, endDate?: string): Promise<HolidayItem[]> => {
    const res = await apiClient.get<HolidayItem[]>('/api/holidays', {
      params: { start_date: startDate, end_date: endDate },
    });
    return res.data;
  },
  create: async (payload: HolidayCreatePayload): Promise<HolidayItem> => {
    const res = await apiClient.post<HolidayItem>('/api/holidays', payload);
    return res.data;
  },
  delete: async (id: number): Promise<{ message: string }> => {
    const res = await apiClient.delete<{ message: string }>(`/api/holidays/${id}`);
    return res.data;
  },
};
