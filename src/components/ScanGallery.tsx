import React from 'react';
import { format } from 'date-fns';
import {
  FileText,
  Download,
  Pencil,
  Eye,
  Grid3X3
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

// Interface Scan pour compatibilité avec l'API
export interface ScanResult {
  diagnosis: string;
  tumorType?: string;
  tumorSize?: string;
  tumorLocation?: string;
  malignant?: boolean;
  notes?: string;
}

export interface Scan {
  id: string;
  patient_id?: string;
  date: string;
  type: string;
  bodyPart: string;
  imageUrl?: string;
  result?: ScanResult;
  doctor?: string;
  facility?: string;
  status: string;
  created_at?: string;
  updated_at?: string;
  // Données étendues pour l'analyse médicale
  volumeAnalysis?: {
    total_tumor_volume_cm3?: number;
    tumor_segments?: Array<{
      type: string;
      volume_cm3: number;
      percentage: number;
      color_code: string;
    }>;
    representative_slices?: number[];
    modalities_used?: string[];
  };
  segmentationResults?: any;
  confidence_score?: number;
}

interface ScanGalleryProps {
  scans: Scan[];
  onSelectScan?: (scan: Scan) => void;
}

const ScanGallery: React.FC<ScanGalleryProps> = ({ scans, onSelectScan }) => {
  // Sort scans by date (newest first)
  const sortedScans = [...scans].sort((a, b) => 
    new Date(b.date).getTime() - new Date(a.date).getTime()
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Galerie des Segmentations</h3>
        <span className="text-sm text-muted-foreground">
          {sortedScans.length} segmentation(s) disponible(s)
        </span>
      </div>

      {sortedScans.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-10">
            <FileText className="h-10 w-10 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">Aucune segmentation disponible</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sortedScans.map((scan) => (
            <Card key={scan.id} className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">
                      Segmentation #{scan.id.slice(-6)}
                    </CardTitle>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant={scan.status === 'COMPLETED' ? 'default' : 'outline'}>
                        {scan.status}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        {format(new Date(scan.date), 'dd/MM/yyyy')}
                      </span>
                    </div>
                  </div>
                  
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon">
                        <Pencil className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => onSelectScan?.(scan)}>
                        <Eye className="mr-2 h-4 w-4" />
                        Voir les images
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        <Download className="mr-2 h-4 w-4" />
                        Télécharger
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </CardHeader>
              
              <CardContent 
                className="space-y-4"
                onClick={() => onSelectScan?.(scan)}
              >
                {/* Informations de la segmentation */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Volume total:</span>
                    <div className="font-medium">{scan.result?.tumorSize || 'Non calculé'}</div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Segments:</span>
                    <div className="font-medium">{scan.result?.tumorLocation || 'Non détectés'}</div>
                  </div>
                </div>
                
                {/* Diagnostic */}
                <div>
                  <span className="text-muted-foreground text-sm">Diagnostic:</span>
                  <p className="font-medium">{scan.result?.diagnosis || 'Non disponible'}</p>
                </div>
                
                {/* Segments détectés */}
                <div>
                  <span className="text-muted-foreground text-sm">Types de segments:</span>
                  <p className="text-sm">{scan.result?.tumorType || 'Non analysés'}</p>
                </div>
                
                {/* Notes techniques */}
                {scan.result?.notes && (
                  <div>
                    <span className="text-muted-foreground text-sm">Notes:</span>
                    <p className="text-sm">{scan.result.notes}</p>
                  </div>
                )}
                
                {/* Bouton d'action principal */}
                <div className="pt-2 border-t">
                  <Button
                    className="w-full"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectScan?.(scan);
                    }}
                  >
                    <Grid3X3 className="mr-2 h-4 w-4" />
                    Galerie d'Images
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default ScanGallery;
