import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cerebloomAPI } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

// Hook pour récupérer les traitements
export const useTreatments = (patientId?: string) => {
  return useQuery({
    queryKey: ['treatments', patientId],
    queryFn: () => cerebloomAPI.getTreatments(patientId),
    enabled: !!patientId, // Ne s'exécute que si patientId est fourni
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook pour créer un traitement
export const useCreateTreatment = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (treatmentData: any) => cerebloomAPI.createTreatment(treatmentData),
    onSuccess: (newTreatment) => {
      // Invalider les queries liées aux traitements
      queryClient.invalidateQueries({ queryKey: ['treatments'] });

      toast({
        title: "Traitement créé",
        description: "Le traitement a été créé avec succès",
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

// Hook pour modifier un traitement
export const useUpdateTreatment = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ id, treatmentData }: { id: string; treatmentData: any }) =>
      cerebloomAPI.updateTreatment(id, treatmentData),
    onSuccess: () => {
      // Invalider les queries liées aux traitements
      queryClient.invalidateQueries({ queryKey: ['treatments'] });

      toast({
        title: "Traitement modifié",
        description: "Le traitement a été modifié avec succès",
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
