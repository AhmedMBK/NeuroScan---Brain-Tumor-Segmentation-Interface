/**
 * 🧠 Composant de workflow de segmentation IA
 * Interface complète pour la segmentation de tumeurs cérébrales
 */

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Brain,
  Upload,
  Play,
  CheckCircle,
  Clock,
  AlertCircle,
  Eye,
  Download,
  FileImage,
  Grid3X3,
  Trash2
} from 'lucide-react';
import ImageUploadForm from '@/components/medical/ImageUploadForm';
import UploadedImagesManager from '@/components/medical/UploadedImagesManager';
import MedicalImageViewer from '@/components/MedicalImageViewer';

import { useSegmentationWorkflow, useSegmentationStatus, useSegmentationResults, useClearSegmentationHistory, useValidateSegmentation } from '@/hooks/useSegmentation';
import { useToast } from '@/hooks/use-toast';

interface SegmentationWorkflowProps {
  patientId: string;
  patientName: string;
}

const SegmentationWorkflow: React.FC<SegmentationWorkflowProps> = ({
  patientId,
  patientName
}) => {
  const { toast } = useToast();
  const [currentSegmentationId, setCurrentSegmentationId] = useState<string | null>(null);
  const [isViewerOpen, setIsViewerOpen] = useState(false);
  const [viewerMode, setViewerMode] = useState<'complete' | 'individual'>('complete');
  const clearHistory = useClearSegmentationHistory();
  const validateSegmentation = useValidateSegmentation();


  const {
    startSegmentation,
    canStartSegmentation,
    isProcessing,
    patientImages,
    patientSegmentations,
    error
  } = useSegmentationWorkflow(patientId);

  const { data: segmentationStatus } = useSegmentationStatus(
    currentSegmentationId || '',
    !!currentSegmentationId
  );

  const { data: segmentationResults } = useSegmentationResults(
    currentSegmentationId || ''
  );

  // Debug: Afficher les résultats dans la console
  React.useEffect(() => {
    if (segmentationResults) {
      console.log('🧠 Résultats de segmentation reçus:', segmentationResults);
      console.log('📊 Structure tumor_analysis:', segmentationResults.tumor_analysis);
      console.log('🎯 Segments tumoraux:', segmentationResults.tumor_analysis?.tumor_segments);
      console.log('🔬 Clinical metrics:', segmentationResults.clinical_metrics);
      console.log('💡 Recommendations:', segmentationResults.recommendations);
      console.log('✅ Status:', segmentationResults.status);

      // Debug détaillé de chaque segment
      if (segmentationResults.tumor_analysis?.tumor_segments) {
        segmentationResults.tumor_analysis.tumor_segments.forEach((segment, index) => {
          console.log(`🔍 Segment ${index + 1}:`, {
            name: segment.name,
            volume: segment.volume_cm3,
            percentage: segment.percentage,

            color: segment.color_code
          });
        });
      }
    }
  }, [segmentationResults]);

  // Rafraîchir l'historique quand une segmentation est terminée
  React.useEffect(() => {
    if (segmentationStatus?.status === 'COMPLETED') {
      patientSegmentations.refetch();
    }
  }, [segmentationStatus?.status, patientSegmentations]);

  const handleStartSegmentation = async () => {
    try {
      const result = await startSegmentation();
      setCurrentSegmentationId(result.segmentation_id);
      toast({
        title: "🧠 Segmentation lancée",
        description: `Analyse en cours avec le modèle U-Net pour ${patientName}`,
      });
    } catch (error) {
      toast({
        title: "Erreur",
        description: error instanceof Error ? error.message : "Erreur lors du lancement",
        variant: "destructive",
      });
    }
  };

  const handleClearHistory = async () => {
    if (!confirm('⚠️ Êtes-vous sûr de vouloir supprimer tout l\'historique des segmentations ? Cette action est irréversible.')) {
      return;
    }

    try {
      await clearHistory.mutateAsync(patientId);
      setCurrentSegmentationId(null); // Reset la sélection
    } catch (error) {
      // L'erreur est déjà gérée par le hook
    }
  };

  const handleValidateSegmentation = async () => {
    if (!currentSegmentationId) {
      toast({
        title: "Aucune segmentation sélectionnée",
        description: "Veuillez sélectionner une segmentation à valider.",
        variant: "destructive",
      });
      return;
    }

    try {
      await validateSegmentation.mutateAsync(currentSegmentationId);
    } catch (error) {
      // L'erreur est déjà gérée par le hook
    }
  };

  const handleDownloadResults = () => {
    if (!currentSegmentationId) {
      toast({
        title: "Aucune segmentation sélectionnée",
        description: "Veuillez sélectionner une segmentation pour télécharger les résultats.",
        variant: "destructive",
      });
      return;
    }

    // Simuler le téléchargement pour l'instant
    toast({
      title: "📥 Téléchargement lancé",
      description: "Les résultats de segmentation sont en cours de téléchargement...",
    });
  };

  const handleGenerateReport = () => {
    if (!currentSegmentationId) {
      toast({
        title: "Aucune segmentation sélectionnée",
        description: "Veuillez sélectionner une segmentation pour générer un rapport.",
        variant: "destructive",
      });
      return;
    }

    // Simuler la génération de rapport pour l'instant
    toast({
      title: "📄 Génération de rapport",
      description: "Le rapport de segmentation est en cours de génération...",
    });
  };

  const handleVisualize = (mode: 'complete' | 'individual' = 'complete') => {
    if (!currentSegmentationId) {
      toast({
        title: "Aucune segmentation sélectionnée",
        description: "Veuillez sélectionner une segmentation à visualiser.",
        variant: "destructive",
      });
      return;
    }

    // Ouvrir le viewer de segmentation avec le mode spécifié
    setViewerMode(mode);
    setIsViewerOpen(true);
  };



  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PROCESSING':
        return <Badge variant="secondary" className="bg-orange-100 text-orange-800">En cours</Badge>;
      case 'COMPLETED':
        return <Badge variant="default" className="bg-green-100 text-green-800">Terminée</Badge>;
      case 'VALIDATED':
        return <Badge variant="default" className="bg-blue-100 text-blue-800">Validée</Badge>;
      case 'FAILED':
        return <Badge variant="destructive">Échec</Badge>;
      default:
        return <Badge variant="outline">Inconnue</Badge>;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'PROCESSING':
        return <Clock className="h-4 w-4 text-orange-500" />;
      case 'COMPLETED':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'VALIDATED':
        return <CheckCircle className="h-4 w-4 text-blue-500" />;
      case 'FAILED':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Brain className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Section Images Médicales */}
      <UploadedImagesManager
        patientId={patientId}
        patientName={patientName}
        imagesData={patientImages.data}
        onRefresh={() => patientImages.refetch()}
        isLoading={patientImages.isLoading}
      />

      {/* Avertissement si pas assez de modalités */}
      {!canStartSegmentation && patientImages.data?.total_images > 0 && (
        <Card className="border-orange-200 bg-orange-50">
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-orange-600" />
              <p className="text-sm text-orange-800">
                ⚠️ Au moins 2 modalités sont requises (FLAIR et T1CE recommandées)
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Lancement de segmentation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-medical" />
            Segmentation IA
          </CardTitle>
          <CardDescription>
            Analyse automatique des tumeurs cérébrales avec modèle U-Net
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Modèle U-Net Kaggle v2.1</p>
              <p className="text-sm text-muted-foreground">
                Segmentation en 3 classes: Nécrose, Œdème, Tumeur rehaussée
              </p>
            </div>
            <Button
              onClick={handleStartSegmentation}
              disabled={!canStartSegmentation || isProcessing}
              className="flex items-center gap-2"
            >
              {isProcessing ? (
                <>
                  <Clock className="h-4 w-4 animate-spin" />
                  Traitement...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  Lancer Segmentation
                </>
              )}
            </Button>
          </div>

          {currentSegmentationId && segmentationStatus && (
            <div className="space-y-3 p-4 border rounded-lg bg-muted/30">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {getStatusIcon(segmentationStatus.status)}
                  <span className="font-medium">Segmentation en cours</span>
                </div>
                {getStatusBadge(segmentationStatus.status)}
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>ID: {currentSegmentationId}</span>
                  <span>Temps estimé: 2-5 minutes</span>
                </div>

                {segmentationStatus.status === 'PROCESSING' && (
                  <Progress value={65} className="w-full" />
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Résultats détaillés de segmentation */}
      {currentSegmentationId && segmentationResults && segmentationResults.status === 'COMPLETED' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              Résultats de Segmentation - {patientName}
            </CardTitle>
            <CardDescription>
              Analyse volumétrique complète des tumeurs détectées
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">

            {/* Debug: Afficher la structure des données */}
            {process.env.NODE_ENV === 'development' && (
              <div className="p-4 bg-gray-100 rounded-lg text-xs">
                <details>
                  <summary className="cursor-pointer font-medium">🔍 Debug - Structure des données</summary>
                  <pre className="mt-2 overflow-auto">
                    {JSON.stringify(segmentationResults, null, 2)}
                  </pre>
                </details>
              </div>
            )}

            {/* Vérification de la structure des données */}
            {!segmentationResults.tumor_analysis && (
              <div className="p-4 bg-yellow-100 border border-yellow-300 rounded-lg">
                <p className="text-yellow-800">
                  ⚠️ Structure de données incomplète : tumor_analysis manquant
                </p>
                <p className="text-xs text-yellow-600 mt-1">
                  Clés disponibles: {Object.keys(segmentationResults).join(', ')}
                </p>
              </div>
            )}

            {segmentationResults.tumor_analysis && !segmentationResults.tumor_analysis.tumor_segments && (
              <div className="p-4 bg-yellow-100 border border-yellow-300 rounded-lg">
                <p className="text-yellow-800">
                  ⚠️ Structure de données incomplète : tumor_segments manquant
                </p>
                <p className="text-xs text-yellow-600 mt-1">
                  Clés tumor_analysis: {Object.keys(segmentationResults.tumor_analysis).join(', ')}
                </p>
              </div>
            )}
            {/* Métriques principales */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold text-medical">
                  {segmentationResults.tumor_analysis?.total_volume_cm3?.toFixed(1) || 'N/A'}
                </div>
                <div className="text-sm text-muted-foreground">Volume total (cm³)</div>
              </div>

              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {segmentationResults.processing_time || 'N/A'}
                </div>
                <div className="text-sm text-muted-foreground">Temps de traitement</div>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {segmentationResults.tumor_analysis?.tumor_segments?.length || 0}
                </div>
                <div className="text-sm text-muted-foreground">Segments détectés</div>
              </div>
            </div>

            {/* Segments tumoraux */}
            {segmentationResults.tumor_analysis?.tumor_segments && (
              <div className="space-y-4">
                <h4 className="font-medium">Analyse des Segments Tumoraux</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {segmentationResults.tumor_analysis.tumor_segments.map((segment: any, index: number) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-center gap-2 mb-3">
                        <div
                          className="w-4 h-4 rounded"
                          style={{ backgroundColor: segment.color_code }}
                        />
                        <span className="font-medium">{segment.name}</span>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">Volume:</span>
                          <span className="font-medium">{typeof segment.volume_cm3 === 'number' ? segment.volume_cm3.toFixed(2) : segment.volume_cm3} cm³</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">Pourcentage:</span>
                          <span className="font-medium">{typeof segment.percentage === 'number' ? segment.percentage.toFixed(1) : segment.percentage}%</span>
                        </div>

                      </div>
                      <p className="text-xs text-muted-foreground mt-2">
                        {segment.description}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}



            {/* Recommandations */}
            {segmentationResults.recommendations && (
              <div className="space-y-4">
                <h4 className="font-medium">Recommandations Cliniques</h4>
                <ul className="space-y-2">
                  {segmentationResults.recommendations.map((recommendation: string, index: number) => (
                    <li key={index} className="flex items-start gap-2 text-sm">
                      <span>{recommendation}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Actions */}
            <Separator />
            <div className="flex flex-wrap gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleVisualize('complete')}
                disabled={!currentSegmentationId || segmentationResults?.status !== 'COMPLETED'}
              >
                <Eye className="h-4 w-4 mr-2" />
                Visualiser
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleDownloadResults}
                disabled={!currentSegmentationId || segmentationResults?.status !== 'COMPLETED'}
              >
                <Download className="h-4 w-4 mr-2" />
                Télécharger
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleGenerateReport}
                disabled={!currentSegmentationId || segmentationResults?.status !== 'COMPLETED'}
              >
                <FileImage className="h-4 w-4 mr-2" />
                Générer rapport
              </Button>
              <Button
                variant="default"
                size="sm"
                onClick={handleValidateSegmentation}
                disabled={!currentSegmentationId || validateSegmentation.isPending || segmentationResults?.status !== 'COMPLETED'}
              >
                {validateSegmentation.isPending ? (
                  <>
                    <Clock className="h-4 w-4 mr-2 animate-spin" />
                    Validation...
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Valider
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Historique des segmentations */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Historique des Segmentations</CardTitle>
              <CardDescription>
                Analyses précédentes pour ce patient
              </CardDescription>
            </div>
            {patientSegmentations.data?.items && patientSegmentations.data.items.length > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleClearHistory}
                disabled={clearHistory.isPending}
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                {clearHistory.isPending ? (
                  <>
                    <Clock className="h-4 w-4 mr-2 animate-spin" />
                    Suppression...
                  </>
                ) : (
                  <>
                    <Trash2 className="h-4 w-4 mr-2" />
                    Supprimer l'historique
                  </>
                )}
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {patientSegmentations.isLoading ? (
            <p className="text-muted-foreground">Chargement de l'historique...</p>
          ) : !patientSegmentations.data?.items || patientSegmentations.data.items.length === 0 ? (
            <p className="text-muted-foreground">Aucune segmentation précédente</p>
          ) : (
            <div className="space-y-2">
              {patientSegmentations.data.items.map((seg: any) => (
                <div
                  key={seg.id}
                  className={`flex items-center justify-between p-2 border rounded cursor-pointer transition-colors hover:bg-muted/50 ${
                    currentSegmentationId === seg.id ? 'bg-blue-50 border-blue-200' : ''
                  }`}
                  onClick={() => setCurrentSegmentationId(seg.id)}
                >
                  <div className="flex items-center gap-2">
                    {getStatusIcon(seg.status)}
                    <div className="flex flex-col">
                      <span className="text-sm">
                        {new Date(seg.started_at).toLocaleDateString()}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        ID: {seg.id.substring(0, 8)}...
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(seg.status)}
                    {currentSegmentationId === seg.id && (
                      <Badge variant="outline" className="text-xs">
                        Sélectionnée
                      </Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Viewer de segmentation avec onglets */}
      {currentSegmentationId && isViewerOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-6xl max-h-[90vh] w-full overflow-hidden">
            <div className="p-4 border-b flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold">Visualisation - {patientName}</h2>
                <p className="text-sm text-muted-foreground">ID: {currentSegmentationId}</p>
              </div>
              <Button variant="outline" onClick={() => setIsViewerOpen(false)}>
                Fermer
              </Button>
            </div>
            <div className="p-4 h-full overflow-auto">
              <MedicalImageViewer
                segmentationId={currentSegmentationId}
                mode={viewerMode}
                onModeChange={setViewerMode}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SegmentationWorkflow;
