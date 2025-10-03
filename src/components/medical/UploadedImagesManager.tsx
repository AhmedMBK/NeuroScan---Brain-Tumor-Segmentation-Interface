import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import {
  FileImage,
  Upload,
  Trash2,
  RefreshCw,
  Calendar,
  HardDrive,
  Eye,
  Download
} from 'lucide-react';
import { format } from 'date-fns';
import { useToast } from '@/hooks/use-toast';
import ImageUploadForm from './ImageUploadForm';
import { cerebloomAPI } from '@/services/api';

interface UploadedImagesManagerProps {
  patientId: string;
  patientName: string;
  imagesData: any;
  onRefresh: () => void;
  isLoading: boolean;
}

const UploadedImagesManager: React.FC<UploadedImagesManagerProps> = ({
  patientId,
  patientName,
  imagesData,
  onRefresh,
  isLoading
}) => {
  const { toast } = useToast();
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);
  const [deletingSeries, setDeletingSeries] = useState<string | null>(null);

  const getModalityColor = (modality: string) => {
    const colors = {
      T1: 'bg-blue-100 text-blue-800 border-blue-200',
      T1CE: 'bg-green-100 text-green-800 border-green-200',
      T2: 'bg-purple-100 text-purple-800 border-purple-200',
      FLAIR: 'bg-orange-100 text-orange-800 border-orange-200',
    };
    return colors[modality as keyof typeof colors] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const handleUploadComplete = (imageIds: string[]) => {
    setIsUploadDialogOpen(false);
    toast({
      title: "Images uploadées",
      description: `${imageIds.length} modalité(s) ajoutée(s) avec succès`,
    });
    onRefresh();
  };

  const handleDeleteSeries = async (seriesId: string) => {
    setDeletingSeries(seriesId);
    try {
      await cerebloomAPI.deleteImageSeries(seriesId);

      toast({
        title: "Série supprimée",
        description: "La série d'images a été supprimée avec succès",
      });
      onRefresh();
    } catch (error) {
      toast({
        title: "Erreur",
        description: error instanceof Error ? error.message : "Erreur lors de la suppression de la série",
        variant: "destructive",
      });
    } finally {
      setDeletingSeries(null);
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileImage className="h-5 w-5" />
            Images Médicales
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-medical"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <FileImage className="h-5 w-5" />
            Images Médicales
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="outline">
              {imagesData?.total_images || 0} modalités
            </Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={onRefresh}
              disabled={isLoading}
            >
              <RefreshCw className="h-3 w-3 mr-1" />
              Actualiser
            </Button>
            <Dialog open={isUploadDialogOpen} onOpenChange={setIsUploadDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="default" size="sm">
                  <Upload className="h-3 w-3 mr-1" />
                  Ajouter
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Upload Images Médicales</DialogTitle>
                  <DialogDescription>
                    Ajoutez les modalités d'images IRM pour {patientName}
                  </DialogDescription>
                </DialogHeader>
                <ImageUploadForm
                  patientId={patientId}
                  onUploadComplete={handleUploadComplete}
                  onCancel={() => setIsUploadDialogOpen(false)}
                />
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {!imagesData?.series || imagesData.series.length === 0 ? (
          <div className="text-center py-8">
            <FileImage className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground mb-4">
              Aucune image uploadée pour ce patient
            </p>
            <Dialog open={isUploadDialogOpen} onOpenChange={setIsUploadDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="outline">
                  <Upload className="h-4 w-4 mr-2" />
                  Uploader des images
                </Button>
              </DialogTrigger>
            </Dialog>
          </div>
        ) : (
          <div className="space-y-4">
            {imagesData.series.map((series: any) => (
              <Card key={series.series_id} className="border-l-4 border-l-medical">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="secondary" className="text-xs">
                          Série {series.series_id.slice(0, 8)}
                        </Badge>
                        {series.acquisition_date && (
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Calendar className="h-3 w-3" />
                            {format(new Date(series.acquisition_date), 'PPP')}
                          </div>
                        )}
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-3">
                        {series.modalities.map((modality: any, index: number) => (
                          <div
                            key={index}
                            className="flex items-center justify-between p-2 border rounded-md"
                          >
                            <Badge className={getModalityColor(modality.modality)}>
                              {modality.modality}
                            </Badge>
                            <div className="flex items-center gap-1 text-xs text-muted-foreground">
                              <HardDrive className="h-3 w-3" />
                              {modality.size_mb} MB
                            </div>
                          </div>
                        ))}
                      </div>

                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <span>Total: {series.total_size_mb} MB</span>
                        <span>Modalités: {series.modalities.length}</span>
                        {series.notes && (
                          <span className="truncate">Notes: {series.notes}</span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-1 ml-4">
                      <Button variant="ghost" size="sm" title="Visualiser">
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm" title="Télécharger">
                        <Download className="h-4 w-4" />
                      </Button>
                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Supprimer la série"
                            disabled={deletingSeries === series.series_id}
                          >
                            {deletingSeries === series.series_id ? (
                              <RefreshCw className="h-4 w-4 animate-spin" />
                            ) : (
                              <Trash2 className="h-4 w-4 text-destructive" />
                            )}
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Supprimer la série d'images</AlertDialogTitle>
                            <AlertDialogDescription>
                              Êtes-vous sûr de vouloir supprimer cette série d'images ?
                              Cette action est irréversible et supprimera toutes les modalités
                              ({series.modalities.map((m: any) => m.modality).join(', ')}).
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Annuler</AlertDialogCancel>
                            <AlertDialogAction
                              onClick={() => handleDeleteSeries(series.series_id)}
                              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                            >
                              Supprimer
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default UploadedImagesManager;
