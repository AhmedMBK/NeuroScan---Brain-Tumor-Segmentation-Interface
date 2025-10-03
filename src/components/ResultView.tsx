
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Brain, CheckCircle, AlertCircle, Info, FileText, ChevronRight, BarChart } from 'lucide-react';
import { Progress } from '@/components/ui/progress';

export interface ClassificationResult {
  tumorType: string;
  confidence: number;
  description: string;
  recommendations: string[];
  imageUrl: string;
}

interface ResultViewProps {
  result: ClassificationResult;
  onReset: () => void;
}

const ResultView = ({ result, onReset }: ResultViewProps) => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<'overview' | 'details'>('overview');

  // Helper function to determine confidence level text and color
  const getConfidenceLevel = (confidence: number) => {
    if (confidence >= 90) {
      return {
        text: t('scans.highConfidence'),
        color: 'text-green-600',
        bgColor: 'bg-green-500',
      };
    } else if (confidence >= 70) {
      return {
        text: t('scans.mediumConfidence'),
        color: 'text-yellow-600',
        bgColor: 'bg-yellow-500',
      };
    } else {
      return {
        text: t('scans.lowConfidence'),
        color: 'text-red-600',
        bgColor: 'bg-red-500',
      };
    }
  };

  const confidenceLevel = getConfidenceLevel(result.confidence);

  return (
    <div className="w-full animate-fade-in">
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-md border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div className="p-6 border-b border-slate-100 dark:border-slate-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-medical/10 dark:bg-medical/20 flex items-center justify-center">
                <Brain className="h-5 w-5 text-medical dark:text-medical-light" />
              </div>
              <h3 className="text-xl font-semibold text-slate-800 dark:text-white">{t('scans.classificationResults')}</h3>
            </div>
            <div>
              <button
                onClick={onReset}
                className="neuro-button-outline py-2 px-4"
              >
                {t('scans.newScan')}
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2">
          <div className="p-6 md:border-r border-slate-100 dark:border-slate-700">
            <div className="aspect-square rounded-lg overflow-hidden bg-slate-50 dark:bg-slate-700 mb-4">
              <img
                src={result.imageUrl}
                alt="Processed MRI Scan"
                className="w-full h-full object-cover"
              />
            </div>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-1">
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-300">{t('scans.confidence')}</p>
                  <p className={`text-sm font-medium ${confidenceLevel.color}`}>
                    {result.confidence}%
                  </p>
                </div>
                <Progress value={result.confidence} className="h-2" indicatorClassName={confidenceLevel.bgColor} />
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  confidenceLevel.text === 'High Confidence'
                    ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                    : confidenceLevel.text === 'Medium Confidence'
                    ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
                    : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                }`}>
                  {confidenceLevel.text}
                </span>
              </div>
            </div>
          </div>

          <div className="p-6">
            <div className="flex space-x-4 mb-6 border-b border-slate-100 dark:border-slate-700">
              <button
                className={`pb-3 text-sm font-medium transition-colors ${
                  activeTab === 'overview'
                    ? 'text-medical dark:text-medical-light border-b-2 border-medical dark:border-medical-light'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
                onClick={() => setActiveTab('overview')}
              >
                {t('classification.overview')}
              </button>
              <button
                className={`pb-3 text-sm font-medium transition-colors ${
                  activeTab === 'details'
                    ? 'text-medical dark:text-medical-light border-b-2 border-medical dark:border-medical-light'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
                onClick={() => setActiveTab('details')}
              >
                {t('classification.details')}
              </button>
            </div>

            {activeTab === 'overview' ? (
              <div className="space-y-6">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="h-5 w-5 text-medical dark:text-medical-light" />
                    <h4 className="text-lg font-semibold text-slate-800 dark:text-white">
                      {result.tumorType}
                    </h4>
                  </div>
                  <p className="text-slate-600 dark:text-slate-300">
                    {result.description}
                  </p>
                </div>

                <div>
                  <h5 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2 flex items-center gap-2">
                    <Info className="h-4 w-4 text-medical dark:text-medical-light" />
                    {t('scans.recommendations')}
                  </h5>
                  <ul className="space-y-2">
                    {result.recommendations.map((recommendation, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm">
                        <ChevronRight className="h-4 w-4 text-medical dark:text-medical-light shrink-0 mt-0.5" />
                        <span className="text-slate-600 dark:text-slate-300">{recommendation}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="glass-card p-4 rounded-lg bg-slate-50/50 dark:bg-slate-700/50 border border-slate-100 dark:border-slate-600">
                  <h5 className="font-medium text-slate-800 dark:text-white mb-2 flex items-center gap-2">
                    <BarChart className="h-4 w-4 text-medical dark:text-medical-light" />
                    {t('scans.tumorCharacteristics')}
                  </h5>
                  <div className="space-y-3">
                    <DetailItem label={t('classification.size')} value="2.3 cm" />
                    <DetailItem label={t('classification.location')} value="Frontal Lobe" />
                    <DetailItem label={t('classification.density')} value="Medium" />
                    <DetailItem label={t('classification.borders')} value="Well Defined" />
                  </div>
                </div>

                <div className="glass-card p-4 rounded-lg bg-slate-50/50 dark:bg-slate-700/50 border border-slate-100 dark:border-slate-600">
                  <h5 className="font-medium text-slate-800 dark:text-white mb-2 flex items-center gap-2">
                    <FileText className="h-4 w-4 text-medical dark:text-medical-light" />
                    {t('scans.technicalDetails')}
                  </h5>
                  <div className="space-y-3">
                    <DetailItem label={t('classification.model')} value="NeuroNet v2.3" />
                    <DetailItem label={t('classification.resolution')} value="1024x1024" />
                    <DetailItem label={t('classification.scanType')} value="T1-weighted MRI" />
                    <DetailItem label={t('classification.processingTime')} value="1.2 seconds" />
                  </div>
                </div>
              </div>
            )}

            <div className="mt-6 pt-6 border-t border-slate-100 dark:border-slate-700">
              <button className="w-full neuro-button-primary flex items-center justify-center gap-2">
                {t('scans.generateReport')} <FileText className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const DetailItem = ({ label, value }: { label: string; value: string }) => (
  <div className="flex justify-between items-center">
    <span className="text-sm text-slate-500 dark:text-slate-400">{label}:</span>
    <span className="text-sm font-medium text-slate-700 dark:text-slate-200">{value}</span>
  </div>
);

export default ResultView;
