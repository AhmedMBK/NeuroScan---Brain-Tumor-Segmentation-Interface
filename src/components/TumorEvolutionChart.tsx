import React, { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  TooltipProps
} from 'recharts';
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
import { Badge } from '@/components/ui/badge';
import { Download, FileText, Info } from 'lucide-react';
import { ChartContainer } from '@/components/ui/chart';
import {
  Tooltip as UITooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface TumorEvolutionChartProps {
  scans: Scan[];
  patientName?: string;
  patientId?: string;
  doctorName?: string;
}

interface ChartData {
  date: string;
  formattedDate: string;
  totalVolume: number;
  necroticVolume: number;
  edemaVolume: number;
  enhancingVolume: number;
  diagnosis: string;
  tumorType: string;
}

const TumorEvolutionChart: React.FC<TumorEvolutionChartProps> = ({
  scans,
  patientName,
  patientId,
  doctorName
}) => {
  const { t } = useTranslation();

  // Filter scans with tumor data and exclude failed segmentations, then sort by date
  const validScans = useMemo(() => {
    return scans
      .filter(scan => {
        // Exclure les segmentations échouées
        const isNotFailed = scan.status !== 'FAILED' &&
                           scan.status !== 'ERROR' &&
                           scan.status !== 'echec' &&
                           scan.status !== 'ECHEC';

        // Vérifier qu'il y a des données de tumeur
        const hasTumorData = scan.result?.tumorSize || scan.volumeAnalysis?.total_tumor_volume_cm3;

        return isNotFailed && hasTumorData;
      })
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  }, [scans]);

  // Prepare comprehensive data for the chart
  const chartData: ChartData[] = useMemo(() => {
    return validScans.map(scan => {
      // Extraire les données de volume depuis les différentes sources possibles
      const volumeAnalysis = (scan as any).volumeAnalysis || {};
      const tumorSegments = volumeAnalysis.tumor_segments || [];

      // Calculer les volumes par segment
      const necroticSegment = tumorSegments.find((s: any) => s.type === 'NECROTIC_CORE');
      const edemaSegment = tumorSegments.find((s: any) => s.type === 'PERITUMORAL_EDEMA');
      const enhancingSegment = tumorSegments.find((s: any) => s.type === 'ENHANCING_TUMOR');

      const totalVolume = volumeAnalysis.total_tumor_volume_cm3 ||
                         parseFloat(scan.result?.tumorSize?.replace('cm³', '').replace('cm', '').trim() || '0');

      return {
        date: scan.date,
        formattedDate: format(new Date(scan.date), 'MMM d, yyyy'),
        totalVolume: totalVolume,
        necroticVolume: necroticSegment?.volume_cm3 || 0,
        edemaVolume: edemaSegment?.volume_cm3 || 0,
        enhancingVolume: enhancingSegment?.volume_cm3 || 0,
        diagnosis: scan.result?.diagnosis || 'N/A',
        tumorType: scan.result?.tumorType || 'Indéterminé'
      };
    });
  }, [validScans]);

  // Custom tooltip component with comprehensive medical data
  const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload as ChartData;
      return (
        <div className="bg-white dark:bg-slate-800 p-4 border rounded-md shadow-lg min-w-[280px]">
          <p className="font-medium text-base mb-2">{data.formattedDate}</p>

          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">{t('scans.totalVolume')}:</span>
              <span className="text-sm font-medium text-medical">{data.totalVolume.toFixed(1)} cm³</span>
            </div>

            {data.enhancingVolume > 0 && (
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">{t('scans.enhancingTumor')}:</span>
                <span className="text-sm font-medium text-blue-600">{data.enhancingVolume.toFixed(1)} cm³</span>
              </div>
            )}

            {data.necroticVolume > 0 && (
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">{t('scans.necroticCore')}:</span>
                <span className="text-sm font-medium text-red-600">{data.necroticVolume.toFixed(1)} cm³</span>
              </div>
            )}

            {data.edemaVolume > 0 && (
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">{t('scans.peritumoralEdema')}:</span>
                <span className="text-sm font-medium text-green-600">{data.edemaVolume.toFixed(1)} cm³</span>
              </div>
            )}

            <div className="pt-2 border-t">
              <p className="text-xs text-muted-foreground">Type: {data.tumorType}</p>
              <p className="text-xs text-muted-foreground mt-1">{data.diagnosis}</p>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  if (validScans.length < 2) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t('scans.tumorEvolution')}</CardTitle>
          <CardDescription>{t('scans.tumorEvolutionDescription')}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center py-10">
          <FileText className="h-10 w-10 text-muted-foreground mb-4" />
          <p className="text-muted-foreground">{t('scans.notEnoughDataForChart')}</p>
        </CardContent>
      </Card>
    );
  }

  // Calculate comprehensive trends
  const firstData = chartData[0];
  const lastData = chartData[chartData.length - 1];
  const volumeTrend = lastData.totalVolume - firstData.totalVolume;
  const volumeTrendPercentage = (volumeTrend / firstData.totalVolume) * 100;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle>{t('scans.tumorEvolution')}</CardTitle>
            <CardDescription>
              {t('scans.tumorEvolutionDescription')}
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
          <TooltipProvider>
            <UITooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Info className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>{t('scans.tumorSizeChartInfo')}</p>
              </TooltipContent>
            </UITooltip>
          </TooltipProvider>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={chartData}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="formattedDate"
                tick={{ fontSize: 12 }}
              />
              <YAxis
                label={{
                  value: 'Volume (cm³)',
                  angle: -90,
                  position: 'insideLeft',
                  style: { textAnchor: 'middle' }
                }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />

              {/* Volume total */}
              <Line
                type="monotone"
                dataKey="totalVolume"
                name={t('scans.totalVolume')}
                stroke="#2563eb"
                activeDot={{ r: 8 }}
                strokeWidth={3}
              />

              {/* Tumeur rehaussée */}
              <Line
                type="monotone"
                dataKey="enhancingVolume"
                name={t('scans.enhancingTumor')}
                stroke="#0080ff"
                activeDot={{ r: 6 }}
                strokeWidth={2}
                strokeDasharray="5 5"
              />

              {/* Noyau nécrotique */}
              <Line
                type="monotone"
                dataKey="necroticVolume"
                name={t('scans.necroticCore')}
                stroke="#dc2626"
                activeDot={{ r: 6 }}
                strokeWidth={2}
                strokeDasharray="3 3"
              />

              {/* Œdème péritumoral */}
              <Line
                type="monotone"
                dataKey="edemaVolume"
                name={t('scans.peritumoralEdema')}
                stroke="#16a34a"
                activeDot={{ r: 6 }}
                strokeWidth={2}
                strokeDasharray="8 2"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Métriques d'évolution complètes */}
        <div className="mt-6 space-y-4">
          <h5 className="font-medium text-sm">{t('scans.tumorEvolutionAnalysis')}</h5>

          {/* Évolution du volume total */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
              <div className="text-xs text-blue-600 dark:text-blue-400 mb-1">{t('scans.initialVolume')}</div>
              <div className="font-medium">{firstData.totalVolume.toFixed(1)} cm³</div>
              <div className="text-xs text-muted-foreground mt-1">
                {format(new Date(firstData.date), 'MMM d, yyyy')}
              </div>
            </div>

            <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
              <div className="text-xs text-blue-600 dark:text-blue-400 mb-1">{t('scans.currentVolume')}</div>
              <div className="font-medium">{lastData.totalVolume.toFixed(1)} cm³</div>
              <div className="text-xs text-muted-foreground mt-1">
                {format(new Date(lastData.date), 'MMM d, yyyy')}
              </div>
            </div>

            <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg">
              <div className="text-xs text-green-600 dark:text-green-400 mb-1">{t('scans.volumeChange')}</div>
              <div className={`font-medium ${volumeTrend < 0 ? 'text-green-600' : volumeTrend > 0 ? 'text-red-600' : 'text-yellow-600'}`}>
                {volumeTrend < 0 ? '↓' : volumeTrend > 0 ? '↑' : '→'} {Math.abs(volumeTrend).toFixed(1)} cm³
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                ({volumeTrendPercentage.toFixed(1)}%)
              </div>
            </div>
          </div>

          {/* Évolution des segments */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">
              <div className="text-xs text-red-600 dark:text-red-400 mb-1">{t('scans.necroticCore')}</div>
              <div className="font-medium">
                {firstData.necroticVolume.toFixed(1)} → {lastData.necroticVolume.toFixed(1)} cm³
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                {((lastData.necroticVolume - firstData.necroticVolume) >= 0 ? '+' : '')}{(lastData.necroticVolume - firstData.necroticVolume).toFixed(1)} cm³
              </div>
            </div>

            <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
              <div className="text-xs text-blue-600 dark:text-blue-400 mb-1">{t('scans.enhancingTumor')}</div>
              <div className="font-medium">
                {firstData.enhancingVolume.toFixed(1)} → {lastData.enhancingVolume.toFixed(1)} cm³
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                {((lastData.enhancingVolume - firstData.enhancingVolume) >= 0 ? '+' : '')}{(lastData.enhancingVolume - firstData.enhancingVolume).toFixed(1)} cm³
              </div>
            </div>

            <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg">
              <div className="text-xs text-green-600 dark:text-green-400 mb-1">{t('scans.peritumoralEdema')}</div>
              <div className="font-medium">
                {firstData.edemaVolume.toFixed(1)} → {lastData.edemaVolume.toFixed(1)} cm³
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                {((lastData.edemaVolume - firstData.edemaVolume) >= 0 ? '+' : '')}{(lastData.edemaVolume - firstData.edemaVolume).toFixed(1)} cm³
              </div>
            </div>
          </div>

          {/* Analyse de l'évolution volumétrique */}
          <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
            <div className="text-sm font-medium mb-2">{t('scans.volumetricEvolutionAnalysis')}</div>
            <div className="text-sm text-muted-foreground">
              {(() => {
                if (volumeTrendPercentage < -20) return t('scans.significantVolumeReduction');
                if (volumeTrendPercentage < -10) return t('scans.moderateVolumeReduction');
                if (volumeTrendPercentage > 25) return t('scans.significantVolumeIncrease');
                if (volumeTrendPercentage > 10) return t('scans.moderateVolumeIncrease');
                return t('scans.stableTumorVolume');
              })()}
            </div>
          </div>
        </div>
      </CardContent>
      <CardFooter>
        <Button variant="outline" size="sm" className="ml-auto">
          <Download className="mr-2 h-4 w-4" />
          {t('scans.exportChart')}
        </Button>
      </CardFooter>
    </Card>
  );
};

export default TumorEvolutionChart;
