import { useState, useEffect, useCallback } from 'react';
import cerebloomAPI from '@/services/api';

export interface ImageData {
  slice: number;
  modality: string;
  filename: string;
  url: string;
}

export interface SegmentationImages {
  segmentation_id: string;
  patient_id: string;
  slices: number[];
  modalities: string[];
  images: ImageData[];
  total_images: number;
}

interface UseSegmentationImagesResult {
  imagesData: SegmentationImages | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  getImageUrl: (slice: number, modality: string) => string | null;
  getAvailableSlices: () => number[];
  getAvailableModalities: () => string[];
}

/**
 * Hook personnalisé pour gérer les images de segmentation individuelles
 */
export const useSegmentationImages = (segmentationId: string): UseSegmentationImagesResult => {
  const [imagesData, setImagesData] = useState<SegmentationImages | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchImagesData = useCallback(async () => {
    if (!segmentationId) return;

    setLoading(true);
    setError(null);

    try {
      // Utiliser les headers d'authentification du service API (comme SegmentationViewer)
      const authHeaders = cerebloomAPI.getAuthHeaders();
      console.log('🔑 Chargement images individuelles pour:', segmentationId);

      const response = await fetch(`/api/v1/segmentation/images/${segmentationId}`, {
        headers: {
          ...authHeaders,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        console.error(`❌ Erreur API ${response.status}:`, response.statusText);

        if (response.status === 401) {
          throw new Error('Session expirée. Veuillez vous reconnecter.');
        } else if (response.status === 403) {
          throw new Error('Accès non autorisé à cette segmentation.');
        } else if (response.status === 404) {
          throw new Error('Images individuelles non trouvées. La segmentation doit être régénérée.');
        } else {
          throw new Error(`Erreur ${response.status}: ${response.statusText}`);
        }
      }

      const data: SegmentationImages = await response.json();
      setImagesData(data);
      console.log('✅ Images individuelles chargées:', data.total_images, 'images');

    } catch (err) {
      console.error('❌ Erreur lors du chargement des images:', err);
      const errorMessage = err instanceof Error ? err.message : 'Erreur inconnue lors du chargement des images';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [segmentationId]);

  // Charger les données au montage et quand l'ID change
  useEffect(() => {
    fetchImagesData();
  }, [fetchImagesData]);

  // Fonction pour obtenir l'URL d'une image spécifique
  const getImageUrl = useCallback((slice: number, modality: string): string | null => {
    if (!imagesData) return null;

    const image = imagesData.images.find(
      img => img.slice === slice && img.modality === modality
    );

    return image ? image.url : null;
  }, [imagesData]);

  // Fonction pour obtenir les slices disponibles
  const getAvailableSlices = useCallback((): number[] => {
    return imagesData?.slices || [];
  }, [imagesData]);

  // Fonction pour obtenir les modalités disponibles
  const getAvailableModalities = useCallback((): string[] => {
    return imagesData?.modalities || [];
  }, [imagesData]);

  return {
    imagesData,
    loading,
    error,
    refetch: fetchImagesData,
    getImageUrl,
    getAvailableSlices,
    getAvailableModalities
  };
};

/**
 * Hook pour gérer l'état de visualisation d'une image
 */
export const useImageViewer = () => {
  const [selectedSlice, setSelectedSlice] = useState<number | null>(null);
  const [selectedModality, setSelectedModality] = useState<string>('t1');
  const [zoomLevel, setZoomLevel] = useState(100);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Contrôles de zoom
  const zoomIn = useCallback(() => {
    setZoomLevel(prev => Math.min(prev + 25, 300));
  }, []);

  const zoomOut = useCallback(() => {
    setZoomLevel(prev => Math.max(prev - 25, 50));
  }, []);

  const resetZoom = useCallback(() => {
    setZoomLevel(100);
  }, []);

  // Contrôle plein écran
  const toggleFullscreen = useCallback(() => {
    setIsFullscreen(prev => !prev);
  }, []);

  // Initialiser la sélection avec les données disponibles
  const initializeSelection = useCallback((slices: number[], modalities: string[]) => {
    if (selectedSlice === null && slices.length > 0) {
      setSelectedSlice(slices[0]);
    }
    
    if (!modalities.includes(selectedModality)) {
      if (modalities.includes('t1')) {
        setSelectedModality('t1');
      } else if (modalities.length > 0) {
        setSelectedModality(modalities[0]);
      }
    }
  }, [selectedSlice, selectedModality]);

  return {
    selectedSlice,
    setSelectedSlice,
    selectedModality,
    setSelectedModality,
    zoomLevel,
    setZoomLevel,
    isFullscreen,
    setIsFullscreen,
    zoomIn,
    zoomOut,
    resetZoom,
    toggleFullscreen,
    initializeSelection
  };
};

/**
 * Constantes pour les modalités
 */
export const MODALITY_CONFIG = {
  LABELS: {
    't1': 'T1',
    't1ce': 'T1CE',
    't2': 'T2',
    'flair': 'FLAIR',
    'segmentation': 'Segmentation',
    'overlay': 'Superposition'
  },
  DESCRIPTIONS: {
    't1': 'Séquence T1 - Anatomie détaillée',
    't1ce': 'T1 avec contraste - Tumeurs rehaussées',
    't2': 'Séquence T2 - Œdème et liquides',
    'flair': 'FLAIR - Suppression du liquide céphalorachidien',
    'segmentation': 'Segmentation IA - Zones tumorales délimitées',
    'overlay': 'Superposition - T1CE + Segmentation'
  },
  COLORS: {
    't1': 'bg-blue-50 text-blue-700',
    't1ce': 'bg-purple-50 text-purple-700',
    't2': 'bg-green-50 text-green-700',
    'flair': 'bg-yellow-50 text-yellow-700',
    'segmentation': 'bg-red-50 text-red-700',
    'overlay': 'bg-orange-50 text-orange-700'
  }
} as const;

/**
 * Utilitaires pour les images
 */
export const imageUtils = {
  /**
   * Génère un nom de fichier pour le téléchargement
   */
  generateDownloadFilename: (
    segmentationId: string, 
    slice?: number, 
    modality?: string, 
    isComplete = false
  ): string => {
    if (isComplete) {
      return `segmentation_${segmentationId}_rapport_complet.png`;
    }
    return `segmentation_${segmentationId}_slice_${slice}_${modality}.png`;
  },

  /**
   * Valide qu'une modalité est supportée
   */
  isValidModality: (modality: string): boolean => {
    return Object.keys(MODALITY_CONFIG.LABELS).includes(modality);
  },

  /**
   * Obtient le label d'une modalité
   */
  getModalityLabel: (modality: string): string => {
    return MODALITY_CONFIG.LABELS[modality as keyof typeof MODALITY_CONFIG.LABELS] || modality;
  },

  /**
   * Obtient la description d'une modalité
   */
  getModalityDescription: (modality: string): string => {
    return MODALITY_CONFIG.DESCRIPTIONS[modality as keyof typeof MODALITY_CONFIG.DESCRIPTIONS] || '';
  },

  /**
   * Obtient la classe CSS de couleur pour une modalité
   */
  getModalityColor: (modality: string): string => {
    return MODALITY_CONFIG.COLORS[modality as keyof typeof MODALITY_CONFIG.COLORS] || 'bg-gray-50 text-gray-700';
  }
};
