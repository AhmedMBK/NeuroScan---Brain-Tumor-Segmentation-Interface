import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cerebloomAPI } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

// Types pour les appointments
export interface AppointmentPatient {
  id: string;
  first_name: string;
  last_name: string;
  email?: string;
}

export interface AppointmentDoctor {
  id: string;
  user: {
    id: string;
    first_name: string;
    last_name: string;
    email: string;
  };
}

export interface Appointment {
  id: string;
  patient_id: string;
  doctor_id: string;
  appointment_date: string;
  appointment_time: string;
  status: 'SCHEDULED' | 'COMPLETED' | 'CANCELLED' | 'NO_SHOW';
  notes?: string;
  appointment_type?: string;
  created_at: string;
  patient?: AppointmentPatient;
  doctor?: AppointmentDoctor;
}

export interface CreateAppointmentData {
  patient_id: string;
  doctor_id: string;
  appointment_date: string;
  appointment_time: string;
  status?: 'SCHEDULED' | 'COMPLETED' | 'CANCELLED' | 'NO_SHOW';
  notes?: string;
  appointment_type?: string;
}

// Hook pour récupérer les rendez-vous
export const useAppointments = (patientId?: string) => {
  return useQuery({
    queryKey: ['appointments', patientId],
    queryFn: () => cerebloomAPI.getAppointments(patientId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook pour créer un rendez-vous
export const useCreateAppointment = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (appointmentData: CreateAppointmentData) => cerebloomAPI.createAppointment(appointmentData),
    onSuccess: (newAppointment) => {
      // Invalider les queries liées aux rendez-vous
      queryClient.invalidateQueries({ queryKey: ['appointments'] });

      toast({
        title: "Rendez-vous créé",
        description: "Le rendez-vous a été créé avec succès",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Erreur",
        description: error.message,
        variant: "destructive",
      });
    },
  });
};

// Hook pour modifier un rendez-vous
export const useUpdateAppointment = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ id, appointmentData }: { id: string; appointmentData: Partial<CreateAppointmentData> }) =>
      cerebloomAPI.updateAppointment(id, appointmentData),
    onSuccess: () => {
      // Invalider les queries liées aux rendez-vous
      queryClient.invalidateQueries({ queryKey: ['appointments'] });

      toast({
        title: "Rendez-vous modifié",
        description: "Le rendez-vous a été modifié avec succès",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Erreur",
        description: error.message,
        variant: "destructive",
      });
    },
  });
};
