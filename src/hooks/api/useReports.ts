import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cerebloomAPI } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

// Types pour les rapports de segmentation
export interface SegmentationReport {
  id: string;
  segmentation_id: string;
  doctor_id: string;
  report_content: string;
  findings?: any;
  recommendations?: any;
  image_attachments?: any;
  template_used?: string;
  quantitative_metrics?: any;
  is_final: boolean;
  created_at: string;
  updated_at: string;
  segmentation?: {
    id: string;
    patient_id: string;
    status: string;
    patient?: {
      first_name: string;
      last_name: string;
      email?: string;
    };
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

export interface CreateSegmentationReportData {
  segmentation_id: string;
  doctor_id?: string;
  report_content: string;
  findings?: any;
  recommendations?: any;
  image_attachments?: any;
  template_used?: string;
  quantitative_metrics?: any;
  is_final?: boolean;
}

// Hook pour récupérer les rapports de segmentation
export const useReports = () => {
  return useQuery({
    queryKey: ['reports'],
    queryFn: () => cerebloomAPI.getReports(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook pour récupérer un rapport spécifique
export const useReport = (reportId: string) => {
  return useQuery({
    queryKey: ['report', reportId],
    queryFn: () => cerebloomAPI.getReport(reportId),
    enabled: !!reportId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook pour créer un rapport de segmentation
export const useCreateReport = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (reportData: CreateSegmentationReportData) => cerebloomAPI.createReport(reportData),
    onSuccess: (newReport) => {
      // Invalider les queries liées aux rapports
      queryClient.invalidateQueries({ queryKey: ['reports'] });

      toast({
        title: "Rapport créé",
        description: "Le rapport de segmentation a été créé avec succès",
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

// Hook pour mettre à jour un rapport
export const useUpdateReport = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ id, reportData }: { id: string; reportData: Partial<CreateSegmentationReportData> }) =>
      cerebloomAPI.updateReport(id, reportData),
    onSuccess: (updatedReport) => {
      // Mettre à jour le cache
      if (updatedReport?.id) {
        queryClient.setQueryData(['report', updatedReport.id], updatedReport);
      }
      queryClient.invalidateQueries({ queryKey: ['reports'] });

      toast({
        title: "Rapport mis à jour",
        description: "Le rapport a été mis à jour avec succès",
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

// Hook pour supprimer un rapport
export const useDeleteReport = () => {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (reportId: string) => cerebloomAPI.deleteReport(reportId),
    onSuccess: () => {
      // Invalider les queries liées aux rapports
      queryClient.invalidateQueries({ queryKey: ['reports'] });

      toast({
        title: "Rapport supprimé",
        description: "Le rapport a été supprimé avec succès",
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

// Hook pour récupérer les rapports d'un patient
export const usePatientReports = (patientId: string) => {
  return useQuery({
    queryKey: ['reports', 'patient', patientId],
    queryFn: () => cerebloomAPI.getPatientReports(patientId),
    enabled: !!patientId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook pour récupérer les rapports d'une segmentation
export const useSegmentationReports = (segmentationId: string) => {
  return useQuery({
    queryKey: ['reports', 'segmentation', segmentationId],
    queryFn: () => cerebloomAPI.getSegmentationReports(segmentationId),
    enabled: !!segmentationId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook pour télécharger un rapport
export const useDownloadReport = () => {
  const { toast } = useToast();

  return useMutation({
    mutationFn: (reportId: string) => cerebloomAPI.downloadReport(reportId),
    onSuccess: () => {
      toast({
        title: "Téléchargement réussi",
        description: "Le rapport a été téléchargé avec succès",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Erreur de téléchargement",
        description: error.message,
        variant: "destructive",
      });
    },
  });
};
