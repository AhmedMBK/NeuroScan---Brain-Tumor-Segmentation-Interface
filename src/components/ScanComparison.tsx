import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';
import {
  ArrowLeft,
  ArrowRight,
  ZoomIn,
  ZoomOut,
  Maximize,
  Minimize,
  Calendar,
  FileText,
  Pencil,
  Download,
  Brain,
  BarChart3,
  TrendingUp,
  TrendingDown,
  Minus,
  Grid3X3,
  Eye,
  RefreshCw
} from 'lucide-react';
import { useSegmentationImages, MODALITY_CONFIG, imageUtils } from '@/hooks/useSegmentationImages';
import { Scan } from '@/components/ScanGallery';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle,
  CardDescription,
  CardFooter
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AspectRatio } from '@/components/ui/aspect-ratio';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';

interface ScanComparisonProps {
  scans: Scan[];
  patientName?: string;
  patientId?: string;
  doctorName?: string;
}

interface SegmentationMetrics {
  totalVolume: number;
  necroticVolume: number;
  edemaVolume: number;
  enhancingVolume: number;
  segments: Array<{
    type: string;
    volume: number;
    percentage: number;
    colorCode: string;
  }>;
}

// Fonction pour extraire les métriques réelles de segmentation
const extractSegmentationMetrics = (scan: Scan): SegmentationMetrics => {
  const volumeAnalysis = scan.volumeAnalysis;
  const segmentationResults = (scan as any).segmentationResults;

  // Volume total depuis différentes sources
  const totalVolume = volumeAnalysis?.total_tumor_volume_cm3 ||
                     segmentationResults?.tumor_analysis?.total_volume_cm3 ||
                     parseFloat(scan.result?.tumorSize?.replace('cm³', '').trim() || '0');

  // Segments depuis volume_analysis ou tumor_analysis
  const tumorSegments = volumeAnalysis?.tumor_segments ||
                       segmentationResults?.tumor_analysis?.tumor_segments || [];

  // Extraire les volumes par type de segment
  const necroticSegment = tumorSegments.find((s: any) => s.type === 'NECROTIC_CORE');
  const edemaSegment = tumorSegments.find((s: any) => s.type === 'PERITUMORAL_EDEMA');
  const enhancingSegment = tumorSegments.find((s: any) => s.type === 'ENHANCING_TUMOR');

  return {
    totalVolume,
    necroticVolume: necroticSegment?.volume_cm3 || 0,
    edemaVolume: edemaSegment?.volume_cm3 || 0,
    enhancingVolume: enhancingSegment?.volume_cm3 || 0,
    segments: tumorSegments.map((s: any) => ({
      type: s.type,
      volume: s.volume_cm3 || 0,
      percentage: s.percentage || 0,
      colorCode: s.color_code || '#666666'
    }))
  };
};

const ScanComparison: React.FC<ScanComparisonProps> = ({
  scans,
  patientName,
  patientId,
  doctorName
}) => {
  const { t } = useTranslation();
  const [leftScanId, setLeftScanId] = useState<string | null>(scans.length > 0 ? scans[1]?.id || null : null);
  const [rightScanId, setRightScanId] = useState<string | null>(scans.length > 0 ? scans[0]?.id || null : null);
  const [zoomLevel, setZoomLevel] = useState<number>(100);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const [comparisonMode, setComparisonMode] = useState<'images' | 'metrics'>('images');

  // États pour la sélection d'images individuelles
  const [leftSlice, setLeftSlice] = useState<number>(50);
  const [leftModality, setLeftModality] = useState<string>('t1');
  const [rightSlice, setRightSlice] = useState<number>(50);
  const [rightModality, setRightModality] = useState<string>('t1');
  
  // Sort scans by date (newest first)
  const sortedScans = [...scans].sort((a, b) =>
    new Date(b.date).getTime() - new Date(a.date).getTime()
  );

  const leftScan = leftScanId ? scans.find(scan => scan.id === leftScanId) : null;
  const rightScan = rightScanId ? scans.find(scan => scan.id === rightScanId) : null;

  // Hooks pour charger les images individuelles
  const leftImages = useSegmentationImages(leftScanId || '');
  const rightImages = useSegmentationImages(rightScanId || '');

  // Extraire les métriques réelles de segmentation
  const leftMetrics = leftScan ? extractSegmentationMetrics(leftScan) : null;
  const rightMetrics = rightScan ? extractSegmentationMetrics(rightScan) : null;

  const handleZoomIn = () => {
    setZoomLevel(Math.min(zoomLevel + 10, 200));
  };

  const handleZoomOut = () => {
    setZoomLevel(Math.max(zoomLevel - 10, 50));
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  // Fonctions pour obtenir les URLs des images individuelles
  const getLeftImageUrl = () => {
    return leftImages.getImageUrl(leftSlice, leftModality);
  };

  const getRightImageUrl = () => {
    return rightImages.getImageUrl(rightSlice, rightModality);
  };

  if (scans.length < 2) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t('scans.scanComparison')}</CardTitle>
          <CardDescription>{t('scans.scanComparisonDescription')}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center py-10">
          <FileText className="h-10 w-10 text-muted-foreground mb-4" />
          <p className="text-muted-foreground">{t('scans.notEnoughScans')}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={isFullscreen ? 'fixed inset-0 z-50 rounded-none' : ''}>
      <CardHeader className="pb-3">
        <div className="flex justify-between items-center mb-4">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              Comparaison des Segmentations
            </CardTitle>
            <CardDescription>
              Comparez les résultats de segmentation entre deux examens
              {patientName && (
                <div className="mt-2 flex items-center gap-4 text-sm">
                  <span className="font-medium text-foreground">
                    Patient: {patientName}
                  </span>
                  {patientId && (
                    <Badge variant="outline" className="bg-medical/10 text-medical border-medical/20">
                      ID: {patientId}
                    </Badge>
                  )}
                  {doctorName && (
                    <span className="text-muted-foreground">
                      Médecin: {doctorName}
                    </span>
                  )}
                </div>
              )}
            </CardDescription>
          </div>
          <div className="flex gap-2">
            {comparisonMode === 'images' && (
              <>
                <Button variant="outline" size="icon" onClick={handleZoomOut} disabled={zoomLevel <= 50}>
                  <ZoomOut className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="icon" onClick={handleZoomIn} disabled={zoomLevel >= 200}>
                  <ZoomIn className="h-4 w-4" />
                </Button>
              </>
            )}
            <Button variant="outline" size="icon" onClick={toggleFullscreen}>
              {isFullscreen ? <Minimize className="h-4 w-4" /> : <Maximize className="h-4 w-4" />}
            </Button>
          </div>
        </div>

        {/* Onglets de mode de comparaison */}
        <Tabs value={comparisonMode} onValueChange={(value) => setComparisonMode(value as 'images' | 'metrics')}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="images" className="flex items-center gap-2">
              <Eye className="h-4 w-4" />
              Images Individuelles
            </TabsTrigger>
            <TabsTrigger value="metrics" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Métriques Détaillées
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </CardHeader>
      <CardContent>
        {/* Sélecteurs de segmentations */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* Left scan selector */}
          <div>
            <label className="text-sm font-medium mb-2 block">Segmentation 1 (Plus récente)</label>
            <Select
              value={leftScanId || ''}
              onValueChange={(value) => setLeftScanId(value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Sélectionner une segmentation" />
              </SelectTrigger>
              <SelectContent>
                {sortedScans.map((scan) => (
                  <SelectItem key={scan.id} value={scan.id}>
                    {format(new Date(scan.date), 'dd/MM/yyyy')} - {scan.result?.tumorSize || 'N/A'}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Right scan selector */}
          <div>
            <label className="text-sm font-medium mb-2 block">Segmentation 2 (Antérieure)</label>
            <Select
              value={rightScanId || ''}
              onValueChange={(value) => setRightScanId(value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Sélectionner une segmentation" />
              </SelectTrigger>
              <SelectContent>
                {sortedScans.map((scan) => (
                  <SelectItem key={scan.id} value={scan.id}>
                    {format(new Date(scan.date), 'dd/MM/yyyy')} - {scan.result?.tumorSize || 'N/A'}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Contenu selon le mode de comparaison */}
        <Tabs value={comparisonMode}>
          <TabsContent value="images">
            {/* Sélecteurs d'images individuelles */}
            <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <h4 className="font-medium mb-4">Sélection des Images à Comparer</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Sélecteurs pour l'image de gauche */}
                  <div className="space-y-3">
                    <h5 className="text-sm font-medium text-muted-foreground">
                      Image 1 - {leftScan ? format(new Date(leftScan.date), 'dd/MM/yyyy') : 'Non sélectionnée'}
                    </h5>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="text-xs font-medium mb-1 block">Coupe</label>
                        <Select value={leftSlice.toString()} onValueChange={(value) => setLeftSlice(parseInt(value))}>
                          <SelectTrigger className="h-8">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {leftImages.getAvailableSlices().map((slice) => (
                              <SelectItem key={slice} value={slice.toString()}>
                                Coupe {slice + 1}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <label className="text-xs font-medium mb-1 block">Modalité</label>
                        <Select value={leftModality} onValueChange={setLeftModality}>
                          <SelectTrigger className="h-8">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {leftImages.getAvailableModalities().map((modality) => (
                              <SelectItem key={modality} value={modality}>
                                {imageUtils.getModalityLabel(modality)}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    {leftImages.loading && (
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <RefreshCw className="h-3 w-3 animate-spin" />
                        Chargement...
                      </div>
                    )}
                  </div>

                  {/* Sélecteurs pour l'image de droite */}
                  <div className="space-y-3">
                    <h5 className="text-sm font-medium text-muted-foreground">
                      Image 2 - {rightScan ? format(new Date(rightScan.date), 'dd/MM/yyyy') : 'Non sélectionnée'}
                    </h5>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="text-xs font-medium mb-1 block">Coupe</label>
                        <Select value={rightSlice.toString()} onValueChange={(value) => setRightSlice(parseInt(value))}>
                          <SelectTrigger className="h-8">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {rightImages.getAvailableSlices().map((slice) => (
                              <SelectItem key={slice} value={slice.toString()}>
                                Coupe {slice + 1}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <label className="text-xs font-medium mb-1 block">Modalité</label>
                        <Select value={rightModality} onValueChange={setRightModality}>
                          <SelectTrigger className="h-8">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {rightImages.getAvailableModalities().map((modality) => (
                              <SelectItem key={modality} value={modality}>
                                {imageUtils.getModalityLabel(modality)}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    {rightImages.loading && (
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <RefreshCw className="h-3 w-3 animate-spin" />
                        Chargement...
                      </div>
                    )}
                  </div>
                </div>
              </div>

            {/* Mode Images */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Image de segmentation 1 */}
              <div>
                {leftScan && (
                  <div className="space-y-3">
                    <div className="relative overflow-hidden rounded-md border bg-gray-50">
                      <div style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: 'top left' }}>
                        <img
                          src={getLeftImageUrl() || '/placeholder-brain-scan.svg'}
                          alt={`Segmentation ${format(new Date(leftScan.date), 'dd/MM/yyyy')}`}
                          className="w-full transition-transform"
                          onError={(e) => {
                            (e.target as HTMLImageElement).src = '/placeholder-brain-scan.svg';
                          }}
                        />
                      </div>
                      <div className="absolute top-2 left-2">
                        <Badge variant="secondary">
                          {format(new Date(leftScan.date), 'dd/MM/yyyy')}
                        </Badge>
                      </div>
                      <div className="absolute top-2 right-2">
                        <Badge variant="outline" className="bg-white/90">
                          {imageUtils.getModalityLabel(leftModality)} - Coupe {leftSlice + 1}
                        </Badge>
                      </div>
                    </div>
                    <div className="text-sm space-y-1">
                      <div className="font-medium">{leftScan.result?.diagnosis || 'N/A'}</div>
                      <div className="text-muted-foreground">
                        Volume: {leftMetrics?.totalVolume.toFixed(1) || 'N/A'} cm³
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Image de segmentation 2 */}
              <div>
                {rightScan && (
                  <div className="space-y-3">
                    <div className="relative overflow-hidden rounded-md border bg-gray-50">
                      <div style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: 'top left' }}>
                        <img
                          src={getRightImageUrl() || '/placeholder-brain-scan.svg'}
                          alt={`Segmentation ${format(new Date(rightScan.date), 'dd/MM/yyyy')}`}
                          className="w-full transition-transform"
                          onError={(e) => {
                            (e.target as HTMLImageElement).src = '/placeholder-brain-scan.svg';
                          }}
                        />
                      </div>
                      <div className="absolute top-2 left-2">
                        <Badge variant="secondary">
                          {format(new Date(rightScan.date), 'dd/MM/yyyy')}
                        </Badge>
                      </div>
                      <div className="absolute top-2 right-2">
                        <Badge variant="outline" className="bg-white/90">
                          {imageUtils.getModalityLabel(rightModality)} - Coupe {rightSlice + 1}
                        </Badge>
                      </div>
                    </div>
                    <div className="text-sm space-y-1">
                      <div className="font-medium">{rightScan.result?.diagnosis || 'N/A'}</div>
                      <div className="text-muted-foreground">
                        Volume: {rightMetrics?.totalVolume.toFixed(1) || 'N/A'} cm³
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="metrics">
            {/* Mode Métriques Détaillées */}
            {leftMetrics && rightMetrics && (
              <div className="space-y-6">
                {/* Résumé de l'évolution */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                    <div className="text-xs text-blue-600 dark:text-blue-400 mb-1">Intervalle</div>
                    <div className="font-medium">
                      {Math.abs(
                        Math.round(
                          (new Date(leftScan!.date).getTime() - new Date(rightScan!.date).getTime()) /
                          (1000 * 60 * 60 * 24)
                        )
                      )} jours
                    </div>
                  </div>

                  <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                    <div className="text-xs text-green-600 dark:text-green-400 mb-1">Évolution Volume</div>
                    <div className="font-medium">
                      {(() => {
                        // Correction: leftMetrics = première colonne, rightMetrics = deuxième colonne
                        // Évolution = de leftMetrics vers rightMetrics
                        const change = rightMetrics.totalVolume - leftMetrics.totalVolume;
                        const changePercent = ((change / leftMetrics.totalVolume) * 100);
                        return (
                          <span className={change < 0 ? 'text-green-600' : change > 0 ? 'text-red-600' : 'text-yellow-600'}>
                            {change < 0 ? <TrendingDown className="inline h-4 w-4 mr-1" /> :
                             change > 0 ? <TrendingUp className="inline h-4 w-4 mr-1" /> :
                             <Minus className="inline h-4 w-4 mr-1" />}
                            {Math.abs(change).toFixed(1)} cm³ ({Math.abs(changePercent).toFixed(1)}%)
                          </span>
                        );
                      })()}
                    </div>
                  </div>

                  <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg">
                    <div className="text-xs text-orange-600 dark:text-orange-400 mb-1">Segments Détectés</div>
                    <div className="font-medium">
                      {leftMetrics.segments.length} / {rightMetrics.segments.length}
                    </div>
                  </div>
                </div>

                {/* Comparaison détaillée des segments */}
                <div className="space-y-4">
                  <h5 className="font-medium text-sm">Comparaison Détaillée des Segments</h5>

                  {/* Tableau de comparaison */}
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse border border-gray-200 dark:border-gray-700">
                      <thead>
                        <tr className="bg-gray-50 dark:bg-gray-800">
                          <th className="border border-gray-200 dark:border-gray-700 p-3 text-left text-sm font-medium">Segment</th>
                          <th className="border border-gray-200 dark:border-gray-700 p-3 text-center text-sm font-medium">
                            {format(new Date(leftScan!.date), 'dd/MM/yyyy')}
                          </th>
                          <th className="border border-gray-200 dark:border-gray-700 p-3 text-center text-sm font-medium">
                            {format(new Date(rightScan!.date), 'dd/MM/yyyy')}
                          </th>
                          <th className="border border-gray-200 dark:border-gray-700 p-3 text-center text-sm font-medium">Évolution</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td className="border border-gray-200 dark:border-gray-700 p-3 font-medium">Volume Total</td>
                          <td className="border border-gray-200 dark:border-gray-700 p-3 text-center">
                            {leftMetrics.totalVolume.toFixed(1)} cm³
                          </td>
                          <td className="border border-gray-200 dark:border-gray-700 p-3 text-center">
                            {rightMetrics.totalVolume.toFixed(1)} cm³
                          </td>
                          <td className="border border-gray-200 dark:border-gray-700 p-3 text-center">
                            {(() => {
                              // Correction: leftMetrics = première colonne, rightMetrics = deuxième colonne
                              // Évolution = de leftMetrics vers rightMetrics
                              const change = rightMetrics.totalVolume - leftMetrics.totalVolume;
                              const changePercent = ((change / leftMetrics.totalVolume) * 100);
                              return (
                                <span className={change < 0 ? 'text-green-600' : change > 0 ? 'text-red-600' : 'text-yellow-600'}>
                                  {change >= 0 ? '+' : ''}{change.toFixed(1)} cm³ ({changePercent.toFixed(1)}%)
                                </span>
                              );
                            })()}
                          </td>
                        </tr>

                        <tr className="bg-red-50 dark:bg-red-900/20">
                          <td className="border border-gray-200 dark:border-gray-700 p-3 font-medium">Noyau Nécrotique</td>
                          <td className="border border-gray-200 dark:border-gray-700 p-3 text-center">
                            {leftMetrics.necroticVolume.toFixed(1)} cm³
                          </td>
                          <td className="border border-gray-200 dark:border-gray-700 p-3 text-center">
                            {rightMetrics.necroticVolume.toFixed(1)} cm³
                          </td>
                          <td className="border border-gray-200 dark:border-gray-700 p-3 text-center">
                            {(() => {
                              // Correction: leftMetrics = première colonne, rightMetrics = deuxième colonne
                              // Évolution = de leftMetrics vers rightMetrics
                              const change = rightMetrics.necroticVolume - leftMetrics.necroticVolume;
                              const changePercent = leftMetrics.necroticVolume > 0 ? ((change / leftMetrics.necroticVolume) * 100) : 0;
                              return (
                                <span className={change < 0 ? 'text-green-600' : change > 0 ? 'text-red-600' : 'text-yellow-600'}>
                                  {change >= 0 ? '+' : ''}{change.toFixed(1)} cm³ ({changePercent.toFixed(1)}%)
                                </span>
                              );
                            })()}
                          </td>
                        </tr>

                        <tr className="bg-blue-50 dark:bg-blue-900/20">
                          <td className="border border-gray-200 dark:border-gray-700 p-3 font-medium">Tumeur Rehaussée</td>
                          <td className="border border-gray-200 dark:border-gray-700 p-3 text-center">
                            {leftMetrics.enhancingVolume.toFixed(1)} cm³
                          </td>
                          <td className="border border-gray-200 dark:border-gray-700 p-3 text-center">
                            {rightMetrics.enhancingVolume.toFixed(1)} cm³
                          </td>
                          <td className="border border-gray-200 dark:border-gray-700 p-3 text-center">
                            {(() => {
                              // Correction: leftMetrics = première colonne, rightMetrics = deuxième colonne
                              // Évolution = de leftMetrics vers rightMetrics
                              const change = rightMetrics.enhancingVolume - leftMetrics.enhancingVolume;
                              const changePercent = leftMetrics.enhancingVolume > 0 ? ((change / leftMetrics.enhancingVolume) * 100) : 0;
                              return (
                                <span className={change < 0 ? 'text-green-600' : change > 0 ? 'text-red-600' : 'text-yellow-600'}>
                                  {change >= 0 ? '+' : ''}{change.toFixed(1)} cm³ ({changePercent.toFixed(1)}%)
                                </span>
                              );
                            })()}
                          </td>
                        </tr>

                        <tr className="bg-green-50 dark:bg-green-900/20">
                          <td className="border border-gray-200 dark:border-gray-700 p-3 font-medium">Œdème Péritumoral</td>
                          <td className="border border-gray-200 dark:border-gray-700 p-3 text-center">
                            {leftMetrics.edemaVolume.toFixed(1)} cm³
                          </td>
                          <td className="border border-gray-200 dark:border-gray-700 p-3 text-center">
                            {rightMetrics.edemaVolume.toFixed(1)} cm³
                          </td>
                          <td className="border border-gray-200 dark:border-gray-700 p-3 text-center">
                            {(() => {
                              // Correction: leftMetrics = première colonne, rightMetrics = deuxième colonne
                              // Évolution = de leftMetrics vers rightMetrics
                              const change = rightMetrics.edemaVolume - leftMetrics.edemaVolume;
                              const changePercent = leftMetrics.edemaVolume > 0 ? ((change / leftMetrics.edemaVolume) * 100) : 0;
                              return (
                                <span className={change < 0 ? 'text-green-600' : change > 0 ? 'text-red-600' : 'text-yellow-600'}>
                                  {change >= 0 ? '+' : ''}{change.toFixed(1)} cm³ ({changePercent.toFixed(1)}%)
                                </span>
                              );
                            })()}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Résumé de l'évolution */}
                <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <h6 className="font-medium text-sm mb-2">Résumé de l'Évolution Volumétrique</h6>
                  <div className="text-sm text-muted-foreground">
                    {(() => {
                      // Correction: leftMetrics = première colonne, rightMetrics = deuxième colonne
                      // Évolution = de leftMetrics vers rightMetrics
                      const volumeChange = ((rightMetrics.totalVolume - leftMetrics.totalVolume) / leftMetrics.totalVolume) * 100;
                      if (volumeChange < -20) return "📉 Réduction volumétrique significative détectée.";
                      if (volumeChange < -10) return "📊 Réduction volumétrique modérée observée.";
                      if (volumeChange > 25) return "⚠️ Augmentation volumétrique importante détectée.";
                      if (volumeChange > 10) return "📈 Augmentation volumétrique modérée observée.";
                      return "📋 Volume tumoral stable entre les segmentations.";
                    })()}
                  </div>
                </div>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
      <CardFooter className="flex justify-between">
        <div className="text-sm text-muted-foreground">
          {comparisonMode === 'images' &&
            `Zoom: ${zoomLevel}% - ${imageUtils.getModalityLabel(leftModality)} vs ${imageUtils.getModalityLabel(rightModality)}`}
          {comparisonMode === 'metrics' && leftMetrics && rightMetrics &&
            `${leftMetrics.segments.length} vs ${rightMetrics.segments.length} segments détectés`}
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Exporter Comparaison
          </Button>
          {comparisonMode === 'images' && (
            <Button variant="outline" size="sm">
              <Pencil className="mr-2 h-4 w-4" />
              Annoter
            </Button>
          )}
        </div>
      </CardFooter>
    </Card>
  );
};

export default ScanComparison;
