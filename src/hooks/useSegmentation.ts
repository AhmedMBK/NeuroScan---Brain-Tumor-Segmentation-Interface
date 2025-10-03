/**
 * 🧠 Hook pour la segmentation IA
 * Intégration avec l'API CereBloom pour la segmentation de tumeurs cérébrales
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import cerebloomAPI, { AISegmentation, TumorSegment, SegmentationResults } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

// Hook pour lancer une segmentation
export const useProcessSegmentation = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (patientId: string) => cerebloomAPI.processPatientSegmentation(patientId),
    onSuccess: (result) => {
      toast({
        title: "🧠 Segmentation lancée",
        description: `Traitement en cours avec le modèle U-Net. ID: ${result.segmentation_id}`,
      });

      // Invalider les segmentations du patient
      queryClient.invalidateQueries({ queryKey: ['patient-segmentations'] });
    },
    onError: (error: Error) => {
      toast({
        title: "Erreur de segmentation",
        description: error.message || "Impossible de lancer la segmentation.",
        variant: "destructive",
      });
    },
  });
};

// Hook pour récupérer le statut d'une segmentation
export const useSegmentationStatus = (segmentationId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['segmentation-status', segmentationId],
    queryFn: () => cerebloomAPI.getSegmentationStatus(segmentationId),
    enabled: enabled && !!segmentationId,
    refetchInterval: (data) => {
      // Refetch toutes les 5 secondes si en cours de traitement
      return data?.status === 'PROCESSING' ? 5000 : false;
    },
  });
};

// Hook pour récupérer les résultats complets d'une segmentation
export const useSegmentationResults = (segmentationId: string) => {
  return useQuery({
    queryKey: ['segmentation-results', segmentationId],
    queryFn: async () => {
      console.log('🔍 Récupération des résultats pour:', segmentationId);
      const results = await cerebloomAPI.getSegmentationResults(segmentationId);
      console.log('📊 Résultats reçus:', results);
      return results;
    },
    enabled: !!segmentationId,
  });
};

// Hook pour récupérer les segments tumoraux
export const useTumorSegments = (segmentationId: string) => {
  return useQuery({
    queryKey: ['tumor-segments', segmentationId],
    queryFn: () => cerebloomAPI.getTumorSegments(segmentationId),
    enabled: !!segmentationId,
  });
};

// Hook pour récupérer les segmentations d'un patient
export const usePatientSegmentations = (patientId: string, page: number = 1) => {
  return useQuery({
    queryKey: ['patient-segmentations', patientId, page],
    queryFn: () => cerebloomAPI.getPatientSegmentations(patientId, page),
    enabled: !!patientId,
  });
};

// Hook pour valider une segmentation (médecins uniquement)
export const useValidateSegmentation = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (segmentationId: string) => cerebloomAPI.validateSegmentation(segmentationId),
    onSuccess: (_, segmentationId) => {
      // Mettre à jour le cache
      queryClient.invalidateQueries({ queryKey: ['segmentation-status', segmentationId] });
      queryClient.invalidateQueries({ queryKey: ['patient-segmentations'] });

      toast({
        title: "✅ Segmentation validée",
        description: "La segmentation a été validée par le médecin.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Erreur de validation",
        description: error.message || "Impossible de valider la segmentation.",
        variant: "destructive",
      });
    },
  });
};

// Hook pour supprimer l'historique des segmentations d'un patient
export const useClearSegmentationHistory = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (patientId: string) => cerebloomAPI.clearPatientSegmentationHistory(patientId),
    onSuccess: (result, patientId) => {
      // Mettre à jour le cache
      queryClient.invalidateQueries({ queryKey: ['patient-segmentations', patientId] });
      queryClient.invalidateQueries({ queryKey: ['segmentation-stats'] });

      toast({
        title: "🗑️ Historique supprimé",
        description: result.message || "L'historique des segmentations a été supprimé.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Erreur de suppression",
        description: error.message || "Impossible de supprimer l'historique.",
        variant: "destructive",
      });
    },
  });
};

// Hook pour les statistiques de segmentation
export const useSegmentationStats = () => {
  return useQuery({
    queryKey: ['segmentation-stats'],
    queryFn: () => cerebloomAPI.getSegmentationStatistics(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

// Hook pour récupérer les segmentations récentes
export const useRecentSegmentations = (limit: number = 5) => {
  return useQuery({
    queryKey: ['recent-segmentations', limit],
    queryFn: async () => {
      // Utiliser l'endpoint existant avec pagination
      const response = await cerebloomAPI.getSegmentations(1, limit, 'started_at', 'desc');
      return response;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook pour upload d'images médicales
export const useUploadMedicalImages = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ patientId, files }: { patientId: string; files: FileList }) =>
      cerebloomAPI.uploadMedicalImages(patientId, files),
    onSuccess: (result, { patientId }) => {
      toast({
        title: "📤 Images uploadées",
        description: `${result.uploaded_count} images ont été uploadées avec succès.`,
      });

      // Invalider les images du patient
      queryClient.invalidateQueries({ queryKey: ['patient-images', patientId] });
    },
    onError: (error: Error) => {
      toast({
        title: "Erreur d'upload",
        description: error.message || "Impossible d'uploader les images.",
        variant: "destructive",
      });
    },
  });
};

// Hook pour récupérer les images d'un patient
export const usePatientImages = (patientId: string) => {
  return useQuery({
    queryKey: ['patient-images', patientId],
    queryFn: () => cerebloomAPI.getPatientImages(patientId),
    enabled: !!patientId,
  });
};

// Hook personnalisé pour le workflow complet de segmentation
export const useSegmentationWorkflow = (patientId: string) => {
  const processSegmentation = useProcessSegmentation();
  const patientImages = usePatientImages(patientId);
  const patientSegmentations = usePatientSegmentations(patientId);

  const canStartSegmentation = patientImages.data?.total_images >= 2; // Au moins 2 modalités

  const startSegmentation = async () => {
    if (!canStartSegmentation) {
      throw new Error('Au moins 2 modalités d\'images sont requises (FLAIR et T1CE recommandées)');
    }

    return processSegmentation.mutateAsync(patientId);
  };

  return {
    startSegmentation,
    canStartSegmentation,
    isProcessing: processSegmentation.isPending,
    patientImages,
    patientSegmentations,
    error: processSegmentation.error,
  };
};
