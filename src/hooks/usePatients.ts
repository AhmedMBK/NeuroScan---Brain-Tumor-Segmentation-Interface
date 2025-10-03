/**
 * 🏥 Hook pour la gestion des patients
 * Intégration avec l'API CereBloom
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import cerebloomAPI, { Patient, PaginatedResponse } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

// Hook pour récupérer la liste des patients
export const usePatients = (page: number = 1, size: number = 10) => {
  return useQuery({
    queryKey: ['patients', page, size],
    queryFn: () => cerebloomAPI.getPatients(page, size),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook pour récupérer un patient spécifique
export const usePatient = (patientId: string) => {
  return useQuery({
    queryKey: ['patient', patientId],
    queryFn: () => cerebloomAPI.getPatient(patientId),
    enabled: !!patientId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook pour récupérer les patients pour les listes déroulantes (selon le rôle)
export const usePatientsForSelect = () => {
  return useQuery({
    queryKey: ['patients-select'],
    queryFn: async () => {
      const response = await cerebloomAPI.getPatients();
      return response.items || [];
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    select: (data) => data.map((patient: any) => ({
      value: patient.id,
      label: `${patient.first_name} ${patient.last_name}`,
      email: patient.email,
      id: patient.id
    }))
  });
};

// Hook pour créer un patient
export const useCreatePatient = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (patientData: Partial<Patient>) => cerebloomAPI.createPatient(patientData),
    onSuccess: (newPatient) => {
      // Invalider et refetch la liste des patients
      queryClient.invalidateQueries({ queryKey: ['patients'] });

      toast({
        title: "Patient créé",
        description: `${newPatient.first_name} ${newPatient.last_name} a été ajouté avec succès.`,
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Erreur",
        description: error.message || "Impossible de créer le patient.",
        variant: "destructive",
      });
    },
  });
};

// Hook pour mettre à jour un patient
export const useUpdatePatient = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Patient> }) =>
      cerebloomAPI.updatePatient(id, data),
    onSuccess: (updatedPatient) => {
      // Mettre à jour le cache
      queryClient.setQueryData(['patient', updatedPatient.id], updatedPatient);
      queryClient.invalidateQueries({ queryKey: ['patients'] });

      toast({
        title: "Patient mis à jour",
        description: `Les informations de ${updatedPatient.first_name} ${updatedPatient.last_name} ont été mises à jour.`,
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Erreur",
        description: error.message || "Impossible de mettre à jour le patient.",
        variant: "destructive",
      });
    },
  });
};

// Hook pour les statistiques des patients
export const usePatientsStats = () => {
  return useQuery({
    queryKey: ['patients-stats'],
    queryFn: () => cerebloomAPI.getDashboardStats(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};
