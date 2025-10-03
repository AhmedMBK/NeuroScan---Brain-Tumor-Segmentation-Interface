import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import cerebloomAPI from '@/services/api';
import { toast } from 'sonner';

// Types pour les secrétaires
export interface Secretary {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  employee_id: string;
  status: 'ACTIVE' | 'INACTIVE';
  assigned_doctor_id: string;
  created_at: string;
}

export interface MySecretariesResponse {
  doctor_id: string;
  doctor_name: string;
  secretaries_count: number;
  secretaries: Secretary[];
}

export interface CreateSecretaryData {
  first_name: string;
  last_name: string;
  email: string;
  username: string;
  password: string;
  phone?: string;
}

export interface CreateSecretaryResponse {
  message: string;
  secretary: {
    id: string;
    first_name: string;
    last_name: string;
    email: string;
    employee_id: string;
    assigned_doctor_id: string;
    username: string;
  };
}

// Hook pour récupérer les secrétaires d'un médecin
export const useMySecretaries = () => {
  return useQuery<MySecretariesResponse>({
    queryKey: ['my-secretaries'],
    queryFn: () => cerebloomAPI.getMySecretaries(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
};

// Hook pour créer une secrétaire
export const useCreateSecretary = () => {
  const queryClient = useQueryClient();

  return useMutation<CreateSecretaryResponse, Error, CreateSecretaryData>({
    mutationFn: (secretaryData: CreateSecretaryData) => 
      cerebloomAPI.createSecretary(secretaryData),
    
    onSuccess: (data) => {
      // Invalider et refetch les données des secrétaires
      queryClient.invalidateQueries({ queryKey: ['my-secretaries'] });
      
      // Afficher un message de succès
      toast.success('Secrétaire créée avec succès', {
        description: `${data.secretary.first_name} ${data.secretary.last_name} a été ajoutée à votre équipe.`,
      });
    },
    
    onError: (error) => {
      console.error('Erreur lors de la création de la secrétaire:', error);
      
      // Afficher un message d'erreur
      toast.error('Erreur lors de la création', {
        description: error.message || 'Impossible de créer la secrétaire. Veuillez réessayer.',
      });
    },
  });
};

// Hook pour mettre à jour une secrétaire
export const useUpdateSecretary = () => {
  const queryClient = useQueryClient();

  return useMutation<Secretary, Error, { id: string; data: Partial<CreateSecretaryData> }>({
    mutationFn: ({ id, data }) => 
      cerebloomAPI.updateUser(id, data), // Utilise l'endpoint users pour la mise à jour
    
    onSuccess: (data) => {
      // Invalider et refetch les données
      queryClient.invalidateQueries({ queryKey: ['my-secretaries'] });
      queryClient.invalidateQueries({ queryKey: ['users'] });
      
      toast.success('Secrétaire mise à jour', {
        description: `Les informations ont été mises à jour avec succès.`,
      });
    },
    
    onError: (error) => {
      console.error('Erreur lors de la mise à jour:', error);
      toast.error('Erreur lors de la mise à jour', {
        description: error.message || 'Impossible de mettre à jour la secrétaire.',
      });
    },
  });
};

// Hook pour supprimer une secrétaire (si nécessaire)
export const useDeleteSecretary = () => {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: (secretaryId: string) => 
      cerebloomAPI.deleteUser(secretaryId), // Utilise l'endpoint users pour la suppression
    
    onSuccess: () => {
      // Invalider et refetch les données
      queryClient.invalidateQueries({ queryKey: ['my-secretaries'] });
      queryClient.invalidateQueries({ queryKey: ['users'] });
      
      toast.success('Secrétaire supprimée', {
        description: 'La secrétaire a été supprimée avec succès.',
      });
    },
    
    onError: (error) => {
      console.error('Erreur lors de la suppression:', error);
      toast.error('Erreur lors de la suppression', {
        description: error.message || 'Impossible de supprimer la secrétaire.',
      });
    },
  });
};
