
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import UploadArea from './UploadArea';
import ResultView, { ClassificationResult } from './ResultView';
import { classifyImage } from '@/utils/classificationService';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Brain, Upload, FileText } from 'lucide-react';

const ClassificationTool = () => {
  const { t } = useTranslation();
  const [file, setFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<ClassificationResult | null>(null);
  const [activeTab, setActiveTab] = useState('upload');

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile);
    handleClassification(selectedFile);
  };

  const handleClassification = async (selectedFile: File) => {
    setIsProcessing(true);
    try {
      // Create a temporary URL for the file
      const imageUrl = URL.createObjectURL(selectedFile);

      // Simulate API call with a delay
      const classificationResult = await classifyImage(imageUrl);

      // Set the result and switch to results tab
      setResult(classificationResult);
      setActiveTab('results');
    } catch (error) {
      console.error('Error during classification:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setResult(null);
    setActiveTab('upload');
  };

  return (
    <section id="classification-tool" className="section bg-slate-50 dark:bg-slate-900">
      <div className="container-custom">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <span className="px-3 py-1 rounded-full bg-medical/10 dark:bg-medical/20 text-medical-dark dark:text-medical-light text-sm font-medium">
            {t('classification.aiPowered')}
          </span>
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mt-4 mb-4">
            {t('classification.title')}
          </h2>
          <p className="text-lg text-slate-600 dark:text-slate-300">
            {t('classification.subtitle')}
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          <Tabs
            value={activeTab}
            onValueChange={setActiveTab}
            className="bg-white dark:bg-slate-800 rounded-xl shadow-md border border-slate-200 dark:border-slate-700 overflow-hidden"
          >
            <div className="px-6 pt-6">
              <TabsList className="grid grid-cols-2 w-full">
                <TabsTrigger value="upload" className="flex items-center gap-2" disabled={isProcessing}>
                  <Upload className="h-4 w-4" />
                  <span>{t('classification.uploadScan')}</span>
                </TabsTrigger>
                <TabsTrigger value="results" className="flex items-center gap-2" disabled={!result}>
                  <Brain className="h-4 w-4" />
                  <span>{t('classification.results')}</span>
                </TabsTrigger>
              </TabsList>
            </div>

            <div className="p-6">
              <TabsContent value="upload" className="mt-0">
                <UploadArea
                  onFileSelect={handleFileSelect}
                  isLoading={isProcessing}
                />
                {isProcessing && (
                  <div className="mt-6 text-center">
                    <div className="inline-block p-3 rounded-full bg-medical/10 dark:bg-medical/20 animate-pulse-scale">
                      <Brain className="h-8 w-8 text-medical dark:text-medical-light animate-pulse" />
                    </div>
                    <p className="mt-4 text-slate-700 dark:text-slate-300">
                      {t('scans.analyzing')}
                    </p>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="results" className="mt-0">
                {result && <ResultView result={result} onReset={handleReset} />}
              </TabsContent>
            </div>
          </Tabs>

          <div className="mt-8 text-center">
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {t('classification.disclaimer')}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ClassificationTool;
