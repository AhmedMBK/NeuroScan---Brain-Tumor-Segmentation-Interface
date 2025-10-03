import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cerebloomAPI } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

// Hook pour récupérer la liste des médecins
export const useDoctors = () => {
  return useQuery({
    queryKey: ['doctors'],
    queryFn: async () => {
      const response = await cerebloomAPI.getDoctors();
      // L'API retourne { doctors: [...] }, on extrait le tableau
      return response.doctors || [];
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook pour récupérer un médecin spécifique
export const useDoctor = (id: string) => {
  return useQuery({
    queryKey: ['doctor', id],
    queryFn: () => cerebloomAPI.getDoctor(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
};

// Hook pour créer un médecin
export const useCreateDoctor = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (doctorData: any) => cerebloomAPI.createDoctor(doctorData),
    onSuccess: (newDoctor) => {
      // Invalider les queries liées aux médecins
      queryClient.invalidateQueries({ queryKey: ['doctors'] });

      toast({
        title: "Médecin créé",
        description: "Le profil médecin a été créé avec succès",
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
