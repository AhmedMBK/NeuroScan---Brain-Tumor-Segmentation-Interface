import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cerebloomAPI } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

// Hook pour vérifier le statut du profil médecin
export const useDoctorProfileStatus = () => {
  return useQuery({
    queryKey: ['doctor-profile-status'],
    queryFn: () => cerebloomAPI.checkDoctorProfileStatus(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook pour compléter le profil médecin
export const useCompleteDoctorProfile = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (profileData: any) => cerebloomAPI.completeDoctorProfile(profileData),
    onSuccess: (newProfile) => {
      // Invalider les queries liées au profil médecin
      queryClient.invalidateQueries({ queryKey: ['doctor-profile-status'] });
      queryClient.invalidateQueries({ queryKey: ['doctors'] });

      toast({
        title: "✅ Profil complété",
        description: "Votre profil médecin a été créé avec succès !",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "❌ Erreur",
        description: error.message || "Erreur lors de la complétion du profil",
        variant: "destructive",
      });
    },
  });
};
