import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { cerebloomAPI } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

export interface UploadImageData {
  patient_id: string;
  acquisition_date?: string;
  notes?: string;
  files: {
    modality: string;
    file: File;
  }[];
}

export interface UploadImageResponse {
  success: boolean;
  message: string;
  series_id: string;
  patient_id: string;
  uploaded_modalities: {
    modality: string;
    filename: string;
    size_mb: number;
    path: string;
  }[];
  total_size_mb: number;
  ready_for_segmentation: boolean;
}

// Hook pour upload d'images médicales
export const useImageUpload = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: async (data: UploadImageData): Promise<UploadImageResponse> => {


      // Passer les données directement - la méthode API créera le FormData
      return cerebloomAPI.uploadMedicalImages(data.patient_id, data);
    },
    onSuccess: (result, variables) => {
      // Invalider les queries liées aux images du patient
      queryClient.invalidateQueries({
        queryKey: ['patient-images', variables.patient_id]
      });
      queryClient.invalidateQueries({
        queryKey: ['patient', variables.patient_id]
      });

      toast({
        title: "Upload réussi",
        description: `${result.images.length} image(s) uploadée(s) avec succès`,
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Erreur d'upload",
        description: error.message || "Erreur lors de l'upload des images",
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
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
