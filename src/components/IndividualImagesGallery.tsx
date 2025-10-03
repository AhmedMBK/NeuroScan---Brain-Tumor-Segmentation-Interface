import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import {
  ArrowLeft,
  Download,
  Eye,
  Grid3X3,
  Loader2,
  ZoomIn,
  ZoomOut,
  Maximize,
  Minimize
} from 'lucide-react';
import { useSegmentationImages, useImageViewer, MODALITY_CONFIG } from '@/hooks/useSegmentationImages';
import InteractiveMedicalImageViewer from '@/components/medical/InteractiveMedicalImageViewer';

interface IndividualImagesGalleryProps {
  segmentationId: string;
  patientName: string;
  onBack: () => void;
}

const IndividualImagesGallery: React.FC<IndividualImagesGalleryProps> = ({
  segmentationId,
  patientName,
  onBack
}) => {
  const [selectedImage, setSelectedImage] = useState<{
    slice: number;
    modality: string;
    filename: string;
    url: string;
  } | null>(null);

  const {
    imagesData,
    loading,
    error,
    refetch,
    getImageUrl
  } = useSegmentationImages(segmentationId);

  const {
    zoomLevel,
    isFullscreen,
    zoomIn,
    zoomOut,
    resetZoom,
    toggleFullscreen
  } = useImageViewer();

  // Grouper les images par slice
  const imagesBySlice = React.useMemo(() => {
    if (!imagesData?.images) return {};
    
    const grouped: Record<number, Array<{
      slice: number;
      modality: string;
      filename: string;
      url: string;
    }>> = {};

    imagesData.images.forEach(image => {
      if (!grouped[image.slice]) {
        grouped[image.slice] = [];
      }
      grouped[image.slice].push(image);
    });

    // Trier les modalités dans chaque slice
    Object.keys(grouped).forEach(slice => {
      grouped[parseInt(slice)].sort((a, b) => {
        const modalityOrder = ['t1', 't1ce', 't2', 'flair', 'segmentation', 'overlay'];
        return modalityOrder.indexOf(a.modality) - modalityOrder.indexOf(b.modality);
      });
    });

    return grouped;
  }, [imagesData]);

  const handleImageClick = (image: any) => {
    setSelectedImage(image);
  };

  const handleDownload = (image: any) => {
    const link = document.createElement('a');
    link.href = image.url;
    link.download = image.filename;
    link.click();
  };

  const getModalityLabel = (modality: string): string => {
    return MODALITY_CONFIG.LABELS[modality as keyof typeof MODALITY_CONFIG.LABELS] || modality.toUpperCase();
  };

  const getModalityColor = (modality: string): string => {
    const colors: Record<string, string> = {
      't1': 'bg-blue-100 text-blue-800',
      't1ce': 'bg-purple-100 text-purple-800',
      't2': 'bg-green-100 text-green-800',
      'flair': 'bg-orange-100 text-orange-800',
      'segmentation': 'bg-red-100 text-red-800',
      'overlay': 'bg-yellow-100 text-yellow-800'
    };
    return colors[modality] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Chargement des images...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <div className="text-red-500 text-4xl mb-4">❌</div>
          <h3 className="text-lg font-medium text-red-600 mb-2">Erreur de chargement</h3>
          <p className="text-sm text-gray-600 mb-4">{error}</p>
          <Button onClick={refetch} variant="outline">
            Réessayer
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={onBack}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour
          </Button>
          <div>
            <h2 className="text-2xl font-bold">Galerie d'Images Individuelles</h2>
            <p className="text-muted-foreground">
              Patient: {patientName} • {imagesData?.total_images || 0} images disponibles
            </p>
          </div>
        </div>
        <Badge variant="secondary" className="flex items-center gap-2">
          <Grid3X3 className="h-4 w-4" />
          {Object.keys(imagesBySlice).length} slices
        </Badge>
      </div>

      {/* Galerie par slice */}
      {Object.entries(imagesBySlice)
        .sort(([a], [b]) => parseInt(a) - parseInt(b))
        .map(([slice, images]) => (
          <Card key={slice}>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">
                Slice {slice}
                <Badge variant="outline" className="ml-2">
                  {images.length} images
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
                {images.map((image) => (
                  <div
                    key={`${image.slice}-${image.modality}`}
                    className="group relative cursor-pointer"
                  >
                    {/* Nom de l'image en haut */}
                    <div className="mb-2 text-center">
                      <Badge className={`text-xs ${getModalityColor(image.modality)}`}>
                        {getModalityLabel(image.modality)}
                      </Badge>
                    </div>
                    
                    {/* Image */}
                    <div 
                      className="relative aspect-square border rounded-lg overflow-hidden bg-gray-50 hover:shadow-lg transition-shadow"
                      onClick={() => handleImageClick(image)}
                    >
                      <img
                        src={image.url}
                        alt={`Slice ${image.slice} - ${getModalityLabel(image.modality)}`}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = '/placeholder-brain-scan.svg';
                        }}
                      />
                      
                      {/* Overlay avec actions */}
                      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleImageClick(image);
                            }}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDownload(image);
                            }}
                          >
                            <Download className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                    
                    {/* Nom du fichier */}
                    <div className="mt-1 text-xs text-center text-muted-foreground truncate">
                      {image.filename}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}

      {/* Viewer modal pour image sélectionnée */}
      {selectedImage && (
        <Dialog open={!!selectedImage} onOpenChange={() => setSelectedImage(null)}>
          <DialogContent className="max-w-4xl max-h-[90vh]">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                {getModalityLabel(selectedImage.modality)} - Slice {selectedImage.slice}
              </DialogTitle>
            </DialogHeader>
            
            <div className="space-y-4">
              {/* Contrôles */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge className={getModalityColor(selectedImage.modality)}>
                    {getModalityLabel(selectedImage.modality)}
                  </Badge>
                  <span className="text-sm text-muted-foreground">
                    Slice {selectedImage.slice}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="icon" onClick={zoomOut}>
                    <ZoomOut className="h-4 w-4" />
                  </Button>
                  <span className="text-sm min-w-[60px] text-center">{zoomLevel}%</span>
                  <Button variant="outline" size="icon" onClick={zoomIn}>
                    <ZoomIn className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" size="icon" onClick={toggleFullscreen}>
                    {isFullscreen ? <Minimize className="h-4 w-4" /> : <Maximize className="h-4 w-4" />}
                  </Button>
                  <Button variant="outline" size="icon" onClick={() => handleDownload(selectedImage)}>
                    <Download className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Image viewer */}
              <div className="relative overflow-hidden rounded-md border bg-gray-50 max-h-[60vh]">
                <InteractiveMedicalImageViewer
                  imageUrl={selectedImage.url}
                  alt={`${getModalityLabel(selectedImage.modality)} - Slice ${selectedImage.slice}`}
                  onDownload={() => handleDownload(selectedImage)}
                />
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

export default IndividualImagesGallery;
