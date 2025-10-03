import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Slider } from '@/components/ui/slider';
import { Card, CardContent } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  ChevronLeft,
  ChevronRight,
  Download,
  ZoomIn,
  ZoomOut,
  RotateCw,
  Eye,
  EyeOff,
  Layers,
  Brain
} from 'lucide-react';
import cerebloomAPI from '@/services/api';
import InteractiveMedicalImageViewer from './InteractiveMedicalImageViewer';

interface SegmentationViewerProps {
  isOpen: boolean;
  onClose: () => void;
  segmentationId: string;
  patientName: string;
}

const SegmentationViewer: React.FC<SegmentationViewerProps> = ({
  isOpen,
  onClose,
  segmentationId,
  patientName
}) => {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getImageUrl = () => {
    const baseUrl = process.env.NODE_ENV === 'development'
      ? 'http://localhost:8000'
      : '';
    // Nouvelle URL simplifiée sans paramètres de coupe
    const url = `${baseUrl}/api/v1/segmentation/visualization/${segmentationId}`;
    console.log('🔍 URL du rapport médical:', url);
    return url;
  };

  const loadImageWithAuth = async () => {
    setIsLoading(true);
    setError(null);

    try {
      console.log('🎨 Chargement du rapport médical...');

      // Utiliser les headers d'authentification du service API
      const authHeaders = cerebloomAPI.getAuthHeaders();
      console.log('🔑 Headers d\'auth:', authHeaders);

      // Ajouter un timestamp pour éviter le cache
      const urlWithTimestamp = `${getImageUrl()}?t=${Date.now()}`;
      console.log('🔍 URL avec timestamp:', urlWithTimestamp);

      const response = await fetch(urlWithTimestamp, {
        method: 'GET',
        headers: {
          ...authHeaders,
          'Accept': 'image/png, image/jpeg, image/*',
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        }
        // credentials: 'include' - Retiré pour éviter le conflit CORS avec wildcard '*'
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ Erreur HTTP ${response.status}:`, errorText);

        if (response.status === 403) {
          throw new Error(`Accès refusé. Veuillez vous reconnecter.`);
        } else if (response.status === 404) {
          throw new Error(`Rapport médical non trouvé. Veuillez relancer la segmentation.`);
        } else if (response.status === 500) {
          throw new Error(`Erreur serveur lors de la génération du rapport.`);
        }

        throw new Error(`Erreur ${response.status}: ${errorText}`);
      }

      // Vérifier que la réponse est bien une image
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.startsWith('image/')) {
        throw new Error(`Type de contenu invalide: ${contentType}. Attendu: image/*`);
      }

      const blob = await response.blob();

      // Nettoyer l'ancienne URL blob si elle existe
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }

      const blobUrl = URL.createObjectURL(blob);
      setImageUrl(blobUrl);
      console.log('✅ Rapport médical chargé avec succès');

    } catch (err) {
      console.error('❌ Erreur chargement rapport médical:', err);
      setError(err instanceof Error ? err.message : 'Erreur inconnue lors du chargement');
    } finally {
      setIsLoading(false);
    }
  };

  // Charger l'image quand le composant s'ouvre
  React.useEffect(() => {
    if (isOpen && segmentationId) {
      loadImageWithAuth();
    }
  }, [isOpen, segmentationId]);

  // Nettoyer l'URL blob quand le composant se démonte
  React.useEffect(() => {
    return () => {
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
    };
  }, [imageUrl]);

  const handleDownloadImage = () => {
    if (imageUrl) {
      // Télécharger l'image blob déjà chargée
      const link = document.createElement('a');
      link.href = imageUrl;
      link.download = `rapport_medical_${segmentationId}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } else {
      // Fallback: télécharger directement depuis l'URL
      const link = document.createElement('a');
      link.href = getImageUrl();
      link.download = `rapport_medical_${segmentationId}.png`;
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-medical" />
            Rapport Médical de Segmentation - {patientName}
          </DialogTitle>
          <DialogDescription>
            ID: {segmentationId} • Rapport médical complet généré par CereBloom
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-4 h-full">
          {/* Barre d'informations */}
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="bg-green-100 text-green-800">
              ✅ Rapport Généré
            </Badge>
            <span className="text-sm text-muted-foreground">
              Rapport médical professionnel avec outils d'analyse interactifs
            </span>
          </div>

          {/* Rapport médical complet */}
          <div className="flex-1">
            <Card className="h-full">
              <CardContent className="p-4 h-full flex items-center justify-center">
                <div className="relative w-full h-full min-h-[600px] flex items-center justify-center">
                      {isLoading && (
                        <div className="flex flex-col items-center gap-4">
                          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-medical"></div>
                          <div className="text-center">
                            <p className="text-lg font-medium">Génération du rapport médical...</p>
                            <p className="text-sm text-muted-foreground">
                              Création des graphiques et métriques de qualité
                            </p>
                          </div>
                        </div>
                      )}

                      {error && (
                        <div className="flex flex-col items-center gap-4 text-center p-8">
                          <div className="text-red-500 text-4xl">📋❌</div>
                          <div>
                            <h3 className="text-lg font-medium text-red-600 mb-2">
                              Erreur de génération du rapport
                            </h3>
                            <p className="text-sm text-gray-600 mb-4">{error}</p>
                            <Button
                              onClick={loadImageWithAuth}
                              variant="outline"
                              size="sm"
                            >
                              🔄 Régénérer le rapport
                            </Button>
                          </div>
                        </div>
                      )}

                  {imageUrl && !isLoading && !error && (
                    <InteractiveMedicalImageViewer
                      imageUrl={imageUrl}
                      alt="Rapport médical de segmentation"
                      onDownload={handleDownloadImage}
                    />
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Informations sur les outils d'analyse */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl mb-2">🔍</div>
                <h4 className="font-medium">Zoom</h4>
                <p className="text-sm text-muted-foreground">
                  Zoom 50% à 300% avec molette ou boutons
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl mb-2">👆</div>
                <h4 className="font-medium">Déplacement</h4>
                <p className="text-sm text-muted-foreground">
                  Cliquer + glisser pour déplacer l'image
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default SegmentationViewer;
