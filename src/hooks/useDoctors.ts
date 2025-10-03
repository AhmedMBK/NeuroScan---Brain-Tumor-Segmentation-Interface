import { useQuery } from '@tanstack/react-query';
import { cerebloomAPI } from '@/services/api';

export const useDoctorsStats = () => {
  return useQuery({
    queryKey: ['doctors', 'statistics'],
    queryFn: () => cerebloomAPI.getDoctorsStats(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useDoctors = () => {
  return useQuery({
    queryKey: ['doctors'],
    queryFn: () => cerebloomAPI.getDoctors(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
