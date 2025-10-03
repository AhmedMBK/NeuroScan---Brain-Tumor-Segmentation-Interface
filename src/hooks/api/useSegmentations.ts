import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cerebloomAPI } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

// Types pour les segmentations
export interface Segmentation {
  id: string;
  patient_id: string;
  doctor_id?: string;
  image_series_id: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  input_parameters?: any;
  segmentation_results?: any;
  volume_analysis?: any;
  tumor_classification?: any;
  confidence_score?: number;
  processing_time?: string;
  started_at: string;
  completed_at?: string;
  validated_at?: string;
  patient?: {
    id: string;
    first_name: string;
    last_name: string;
    email?: string;
  };
  doctor?: {
    id: string;
    user: {
      first_name: string;
      last_name: string;
      email: string;
    };
  };
}

// Hook pour récupérer les segmentations
export const useSegmentations = (patientId?: string) => {
  return useQuery({
    queryKey: ['segmentations', patientId],
    queryFn: () => cerebloomAPI.getSegmentations(patientId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook pour récupérer une segmentation spécifique
export const useSegmentation = (segmentationId: string) => {
  return useQuery({
    queryKey: ['segmentation', segmentationId],
    queryFn: () => cerebloomAPI.getSegmentation(segmentationId),
    enabled: !!segmentationId,
    staleTime: 5 * 60 * 1000,
  });
};

// Hook pour récupérer les segmentations pour les listes déroulantes
export const useSegmentationsForSelect = (patientId?: string) => {
  return useQuery({
    queryKey: ['segmentations-select', patientId],
    queryFn: async () => {
      if (!patientId) {
        return [];
      }
      const segmentations = await cerebloomAPI.getSegmentations(patientId);
      return segmentations || [];
    },
    enabled: !!patientId, // Ne pas exécuter si patientId est vide
    staleTime: 5 * 60 * 1000,
    select: (data) => data
      .filter((seg: Segmentation) => seg.status === 'COMPLETED')
      .map((seg: Segmentation) => ({
        value: seg.id,
        label: `Segmentation ${seg.id.slice(0, 8)} - ${seg.patient?.first_name} ${seg.patient?.last_name}`,
        patient_id: seg.patient_id,
        completed_at: seg.completed_at,
        id: seg.id
      }))
  });
};

// Hook pour créer une segmentation
export const useCreateSegmentation = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (segmentationData: any) => cerebloomAPI.createSegmentation(segmentationData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['segmentations'] });
      toast({
        title: "Segmentation créée",
        description: "La segmentation a été créée avec succès",
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

// Hook pour mettre à jour une segmentation
export const useUpdateSegmentation = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ id, segmentationData }: { id: string; segmentationData: any }) =>
      cerebloomAPI.updateSegmentation(id, segmentationData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['segmentations'] });
      toast({
        title: "Segmentation mise à jour",
        description: "La segmentation a été mise à jour avec succès",
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
