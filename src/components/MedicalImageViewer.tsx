import React, { useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import {
  ZoomIn,
  ZoomOut,
  Download,
  Maximize,
  Minimize,
  Eye,
  Grid3X3,
  Loader2,
  RefreshCw
} from 'lucide-react';
import { useSegmentationImages, useImageViewer, MODALITY_CONFIG, imageUtils } from '@/hooks/useSegmentationImages';

interface MedicalImageViewerProps {
  segmentationId: string;
  mode?: 'complete' | 'individual';
  className?: string;
  onModeChange?: (mode: 'complete' | 'individual') => void;
}

const MedicalImageViewer: React.FC<MedicalImageViewerProps> = ({
  segmentationId,
  mode = 'complete',
  className = '',
  onModeChange
}) => {
  // Hooks personnalisés
  const {
    imagesData,
    loading,
    error,
    refetch,
    getImageUrl,
    getAvailableSlices,
    getAvailableModalities
  } = useSegmentationImages(mode === 'individual' ? segmentationId : '');

  const {
    selectedSlice,
    setSelectedSlice,
    selectedModality,
    setSelectedModality,
    zoomLevel,
    isFullscreen,
    zoomIn,
    zoomOut,
    resetZoom,
    toggleFullscreen,
    initializeSelection
  } = useImageViewer();

  // Initialiser la sélection quand les données sont chargées
  useEffect(() => {
    if (imagesData && mode === 'individual') {
      initializeSelection(imagesData.slices, imagesData.modalities);
    }
  }, [imagesData, mode, initializeSelection]);

  // Obtenir l'URL de l'image actuelle
  const getCurrentImageUrl = () => {
    if (mode === 'complete') {
      return `/api/v1/segmentation/visualization-temp/${segmentationId}`;
    }

    if (selectedSlice === null) return null;
    return getImageUrl(selectedSlice, selectedModality);
  };
  
  // Télécharger l'image
  const handleDownload = () => {
    const imageUrl = getCurrentImageUrl();
    if (imageUrl) {
      const link = document.createElement('a');
      link.href = imageUrl;
      link.download = imageUtils.generateDownloadFilename(
        segmentationId,
        selectedSlice || undefined,
        selectedModality,
        mode === 'complete'
      );
      link.click();
    }
  };
  
  const currentImageUrl = getCurrentImageUrl();
  
  return (
    <Card className={`${className} ${isFullscreen ? 'fixed inset-0 z-50 rounded-none overflow-auto' : 'max-h-[90vh] overflow-auto'}`}>
      <CardHeader className="pb-3 sticky top-0 bg-white z-10 border-b">
        <div className="flex justify-between items-center">
          <CardTitle className="flex items-center gap-2">
            <Eye className="h-5 w-5" />
            Visualiseur Médical
          </CardTitle>

          {/* Contrôles d'affichage */}
          <div className="flex gap-2">
            <Button variant="outline" size="icon" onClick={zoomOut} disabled={zoomLevel <= 50}>
              <ZoomOut className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon" onClick={resetZoom}>
              <span className="text-xs font-medium">{zoomLevel}%</span>
            </Button>
            <Button variant="outline" size="icon" onClick={zoomIn} disabled={zoomLevel >= 300}>
              <ZoomIn className="h-4 w-4" />
            </Button>
            {mode === 'individual' && error && (
              <Button variant="outline" size="icon" onClick={refetch}>
                <RefreshCw className="h-4 w-4" />
              </Button>
            )}
            <Button variant="outline" size="icon" onClick={handleDownload} disabled={!currentImageUrl}>
              <Download className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon" onClick={toggleFullscreen}>
              {isFullscreen ? <Minimize className="h-4 w-4" /> : <Maximize className="h-4 w-4" />}
            </Button>

          </div>
        </div>

        {/* Onglets de mode */}
        <Tabs value={mode} onValueChange={onModeChange} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="complete" className="flex items-center gap-2">
              <Grid3X3 className="h-4 w-4" />
              Rapport Complet
            </TabsTrigger>
            <TabsTrigger value="individual" className="flex items-center gap-2">
              <Eye className="h-4 w-4" />
              Images Individuelles
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </CardHeader>

      <CardContent className="pb-6">
        <Tabs value={mode}>
          {/* Mode Rapport Complet */}
          <TabsContent value="complete">
            <div className="space-y-4">
              <div className="text-center">
                <Badge variant="secondary">Rapport Médical Complet</Badge>
                <p className="text-sm text-muted-foreground mt-1">
                  Vue d'ensemble avec toutes les modalités et slices
                </p>
              </div>
              
              <div className="relative rounded-md border bg-gray-50 min-h-[600px] w-full flex items-center justify-center">
                <div
                  style={{
                    transform: `scale(${zoomLevel / 100})`,
                    transformOrigin: 'center center',
                    transition: 'transform 0.2s ease'
                  }}
                >
                  <img
                    src={`/api/v1/segmentation/visualization-temp/${segmentationId}`}
                    alt="Rapport médical complet"
                    className="block"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = '/placeholder-brain-scan.svg';
                    }}
                  />
                </div>
              </div>
            </div>
          </TabsContent>
          
          {/* Mode Images Individuelles */}
          <TabsContent value="individual">
            {loading && (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin mr-2" />
                <span>Chargement des images...</span>
              </div>
            )}
            
            {error && (
              <div className="text-center py-8">
                <p className="text-red-600 mb-2">Erreur: {error}</p>
                <Button onClick={refetch} variant="outline">
                  Réessayer
                </Button>
              </div>
            )}
            
            {imagesData && !loading && !error && (
              <div className="space-y-6">
                {/* Sélecteurs */}
                <div className="bg-gray-50 p-4 rounded-lg border">
                  <h3 className="text-sm font-semibold mb-3 text-gray-700">Sélection d'image</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium mb-2 block">Coupe (Slice)</label>
                      <Select
                        value={selectedSlice?.toString() || ''}
                        onValueChange={(value) => setSelectedSlice(parseInt(value))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Sélectionner une coupe" />
                        </SelectTrigger>
                        <SelectContent>
                          {imagesData.slices.map((slice) => (
                            <SelectItem key={slice} value={slice.toString()}>
                              Coupe {slice + 1} (Index {slice})
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <label className="text-sm font-medium mb-2 block">Modalité</label>
                      <Select
                        value={selectedModality}
                        onValueChange={setSelectedModality}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Sélectionner une modalité" />
                        </SelectTrigger>
                        <SelectContent>
                          {imagesData.modalities.map((modality) => (
                            <SelectItem key={modality} value={modality}>
                              <div className="flex flex-col">
                                <span className="font-medium">
                                  {imageUtils.getModalityLabel(modality)}
                                </span>
                                <span className="text-xs text-muted-foreground">
                                  {imageUtils.getModalityDescription(modality)}
                                </span>
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  {/* Informations sur la sélection */}
                  {selectedSlice !== null && (
                    <div className="flex items-center gap-2 flex-wrap mt-3 pt-3 border-t">
                      <Badge variant="outline">
                        Coupe {selectedSlice + 1}
                      </Badge>
                      <Badge
                        variant="outline"
                        className={imageUtils.getModalityColor(selectedModality)}
                      >
                        {imageUtils.getModalityLabel(selectedModality)}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        {imageUtils.getModalityDescription(selectedModality)}
                      </span>
                    </div>
                  )}
                </div>

                {/* Image sélectionnée */}
                <div className="bg-white border rounded-lg p-4">
                  <h3 className="text-sm font-semibold mb-3 text-gray-700">Aperçu de l'image</h3>
                  {currentImageUrl ? (
                    <div className="relative rounded-md border bg-gray-50 h-[350px] w-full overflow-hidden flex items-center justify-center">
                      <img
                        src={currentImageUrl}
                        alt={`Coupe ${selectedSlice} - ${selectedModality}`}
                        className="max-w-full max-h-full object-contain"
                        style={{
                          transform: `scale(${zoomLevel / 100})`,
                          transformOrigin: 'center center',
                          transition: 'transform 0.2s ease'
                        }}
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = '/placeholder-brain-scan.svg';
                        }}
                      />
                    </div>
                  ) : (
                    <div className="text-center py-6 h-[350px] flex flex-col items-center justify-center border rounded-md bg-gray-50">
                      <Grid3X3 className="h-8 w-8 text-muted-foreground mb-2" />
                      <p className="text-sm text-muted-foreground">
                        Sélectionnez une coupe et modalité
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default MedicalImageViewer;
