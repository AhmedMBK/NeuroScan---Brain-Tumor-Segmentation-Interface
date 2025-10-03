import React, { useState, useRef, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ZoomIn, ZoomOut, RefreshCw, Download } from 'lucide-react';

interface InteractiveMedicalImageViewerProps {
  imageUrl: string;
  alt: string;
  onDownload?: () => void;
}

const InteractiveMedicalImageViewer: React.FC<InteractiveMedicalImageViewerProps> = ({
  imageUrl,
  alt,
  onDownload
}) => {
  // États simplifiés
  const [zoom, setZoom] = useState(100);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [fitToContainer, setFitToContainer] = useState(true);

  // Références
  const containerRef = useRef<HTMLDivElement>(null);

  // Fonctions de zoom
  const handleZoomIn = useCallback(() => {
    setFitToContainer(false);
    setZoom(prev => Math.min(prev + 25, 300));
  }, []);

  const handleZoomOut = useCallback(() => {
    setFitToContainer(false);
    setZoom(prev => Math.max(prev - 25, 50));
  }, []);

  const handleZoomReset = useCallback(() => {
    setZoom(100);
    setPosition({ x: 0, y: 0 });
    setFitToContainer(true);
  }, []);

  // Fonctions de déplacement
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button === 0) { // Clic gauche seulement
      setFitToContainer(false);
      setIsDragging(true);
      setDragStart({
        x: e.clientX - position.x,
        y: e.clientY - position.y
      });
    }
  }, [position]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (isDragging) {
      setPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  }, [isDragging, dragStart]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Zoom avec la molette
  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    setFitToContainer(false);
    const delta = e.deltaY > 0 ? -10 : 10;
    setZoom(prev => Math.max(50, Math.min(300, prev + delta)));
  }, []);

  const imageStyle = fitToContainer ? {
    // Mode adapté au conteneur (par défaut) - image à taille normale
    maxWidth: '100%',
    maxHeight: '100%',
    width: 'auto',
    height: 'auto',
    cursor: 'grab',
    userSelect: 'none' as const,
    objectFit: 'contain' as const
  } : {
    // Mode zoom/déplacement interactif - utilise le zoom à partir de la taille adaptée
    transform: `translate(${position.x}px, ${position.y}px) scale(${zoom / 100})`,
    cursor: isDragging ? 'grabbing' : 'grab',
    transition: isDragging ? 'none' : 'transform 0.2s ease-out',
    maxWidth: '100%',
    maxHeight: '100%',
    objectFit: 'contain' as const,
    userSelect: 'none' as const,
    pointerEvents: 'auto' as const
  };

  return (
    <div className="relative w-full h-full min-h-[600px]">
      {/* Barre d'outils simplifiée */}
      <div className="flex items-center gap-2 p-3 bg-background border-b">
        {/* Zoom */}
        <div className="flex items-center gap-1">
          <Button variant="outline" size="sm" onClick={handleZoomOut} disabled={zoom <= 50}>
            <ZoomOut className="h-4 w-4" />
          </Button>
          <Badge variant="secondary" className="min-w-[60px] text-center">
            {zoom}%
          </Badge>
          <Button variant="outline" size="sm" onClick={handleZoomIn} disabled={zoom >= 300}>
            <ZoomIn className="h-4 w-4" />
          </Button>
        </div>

        <Button variant="outline" size="sm" onClick={handleZoomReset}>
          <RefreshCw className="h-4 w-4" />
          Reset
        </Button>

        {onDownload && (
          <Button variant="outline" size="sm" onClick={onDownload}>
            <Download className="h-4 w-4" />
            Télécharger
          </Button>
        )}
      </div>

      {/* Zone d'affichage de l'image */}
      <div
        ref={containerRef}
        className="relative flex-1 overflow-hidden bg-gray-50 dark:bg-gray-900"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        style={{ height: '600px' }}
      >
        <div className="absolute inset-0 flex items-center justify-center">
          <img
            src={imageUrl}
            alt={alt}
            style={imageStyle}
            className="block"
            draggable={false}
            onError={(e) => {
              console.error('Erreur chargement image:', e);
              console.error('URL de l\'image:', imageUrl);
            }}
            onLoad={() => {
              console.log('✅ Image chargée avec succès:', imageUrl);
            }}
          />
        </div>

        {/* Aide simple */}
        <div className="absolute bottom-4 right-4 bg-black/70 text-white px-3 py-2 rounded text-xs">
          <div>Clic + glisser pour déplacer | Molette pour zoomer</div>
        </div>
      </div>
    </div>
  );
};

export default InteractiveMedicalImageViewer;
