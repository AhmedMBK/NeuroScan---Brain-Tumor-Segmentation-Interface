import React, { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  ArrowLeft,
  FileText,
  Brain,
  Calendar,
  Upload,
  BarChart,
  SplitSquareVertical,
  Grid,
  Layers
} from 'lucide-react';
import { usePatient } from '@/hooks/usePatients';
import { usePatientImages } from '@/hooks/api/useImageUpload';
import { usePatientSegmentations } from '@/hooks/useSegmentation';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import ScanGallery, { Scan } from '@/components/ScanGallery';
import ScanComparison from '@/components/ScanComparison';
import TumorEvolutionChart from '@/components/TumorEvolutionChart';
import IndividualImagesGallery from '@/components/IndividualImagesGallery';

// Fonction pour transformer les segmentations vers le format Scan
const transformSegmentationsToScans = (segmentations: any[]): Scan[] => {
  if (!segmentations || !Array.isArray(segmentations)) return [];

  // Filtrer les segmentations pour exclure celles avec l'état "échec"
  const validSegmentations = segmentations.filter(segmentation =>
    segmentation.status !== 'FAILED' &&
    segmentation.status !== 'ERROR' &&
    segmentation.status !== 'echec' &&
    segmentation.status !== 'ECHEC'
  );

  return validSegmentations.map((segmentation, index) => {
    // Calculer les informations de la tumeur depuis l'analyse volumétrique
    const volumeAnalysis = segmentation.volume_analysis;
    const segmentationResults = segmentation.segmentation_results;
    const tumorAnalysis = segmentationResults?.tumor_analysis;

    // Le volume total peut être dans volume_analysis OU segmentation_results.tumor_analysis
    const totalVolume = tumorAnalysis?.total_volume_cm3 ||
                       volumeAnalysis?.total_tumor_volume_cm3 ||
                       volumeAnalysis?.total_volume_cm3 || 0;

    // Analyser les segments détectés par le modèle de segmentation
    const tumorSegments = tumorAnalysis?.tumor_segments || volumeAnalysis?.tumor_segments || [];

    // Créer un résumé des segments détectés (pas de classification médicale)
    let segmentsSummary = 'Aucun segment détecté';
    if (tumorSegments.length > 0) {
      const segmentTypes = tumorSegments.map((s: any) => {
        switch(s.type) {
          case 'ENHANCING_TUMOR': return 'Tumeur rehaussée';
          case 'NECROTIC_CORE': return 'Noyau nécrotique';
          case 'PERITUMORAL_EDEMA': return 'Œdème péritumoral';
          default: return s.type;
        }
      });
      segmentsSummary = segmentTypes.join(', ');
    }

    return {
      id: segmentation.id || `segmentation-${index}`,
      patient_id: segmentation.patient_id,
      date: segmentation.started_at?.split('T')[0] || new Date().toISOString().split('T')[0],
      type: 'Segmentation IA',
      bodyPart: 'Cerveau',
      imageUrl: `/api/segmentation/${segmentation.id}/visualization/complete_report.png`, // Vraie image de segmentation
      result: {
        diagnosis: `Segmentation automatique: ${totalVolume.toFixed(1)} cm³`,
        tumorType: segmentsSummary,
        tumorSize: `${totalVolume.toFixed(1)} cm³`,
        tumorLocation: `${tumorSegments.length} segment(s) détecté(s)`,
        malignant: undefined, // Pas de classification médicale
        notes: `Segmentation ${segmentation.status}. Temps: ${segmentation.processing_time || 'N/A'}`
      },
      doctor: segmentation.doctor_id || 'IA CereBloom',
      facility: 'CereBloom',
      status: segmentation.status === 'COMPLETED' ? 'Completed' : segmentation.status,
      created_at: segmentation.started_at,
      updated_at: segmentation.completed_at || segmentation.started_at,
      // Ajouter les données complètes pour les composants d'évolution
      volumeAnalysis: {
        total_tumor_volume_cm3: totalVolume,
        tumor_segments: tumorSegments,
        modalities_used: volumeAnalysis?.modalities_used || [],
        representative_slices: volumeAnalysis?.representative_slices || []
      },
      segmentationResults: segmentationResults
    };
  });
};

const PatientExamHistory: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [activeTab, setActiveTab] = useState<string>('gallery');
  const [selectedScan, setSelectedScan] = useState<Scan | null>(null);
  const [showGallery, setShowGallery] = useState(false);

  // Utiliser les vraies API
  const { data: patient, isLoading, error } = usePatient(id || '');

  // Récupérer les images et segmentations du patient
  const { data: patientImages, isLoading: imagesLoading } = usePatientImages(id || '');
  const { data: segmentationsData, isLoading: segmentationsLoading } = usePatientSegmentations(id || '');

  // Transformer les données pour compatibilité avec les composants existants
  const segmentations = segmentationsData?.items || segmentationsData?.results || [];
  const scans = transformSegmentationsToScans(segmentations);

  // Fonction pour gérer la sélection d'une segmentation
  const handleScanSelect = (scan: Scan) => {
    setSelectedScan(scan);
    setShowGallery(true);
  };

  if (error) {
    toast({
      variant: 'destructive',
      title: t('common.error'),
      description: t('patients.patientNotFound'),
    });
    navigate('/patients');
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-medical"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (!patient) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="text-center">
            <h2 className="text-2xl font-bold">{t('patients.patientNotFound')}</h2>
            <p className="text-muted-foreground mt-2">{t('patients.patientNotFoundDescription')}</p>
            <Button asChild className="mt-4">
              <Link to="/patients">
                <ArrowLeft className="mr-2 h-4 w-4" />
                {t('common.back')}
              </Link>
            </Button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
          <div className="flex items-center gap-2">
            <Button variant="outline" size="icon" asChild className="h-8 w-8">
              <Link to={`/patients/${patient.id}`}>
                <ArrowLeft className="h-4 w-4" />
              </Link>
            </Button>
            <h1 className="text-2xl font-bold tracking-tight">{t('scans.examHistory')}</h1>
          </div>
          <div className="flex gap-2 mt-4 md:mt-0">
            <Button variant="outline" asChild>
              <Link to={`/patients/${patient.id}`}>
                <FileText className="mr-2 h-4 w-4" />
                {t('patients.patientDetails')}
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link to={`/patients/${patient.id}/treatment-tracking`}>
                <Calendar className="mr-2 h-4 w-4" />
                {t('treatments.treatmentTracking')}
              </Link>
            </Button>
            <Button>
              <Upload className="mr-2 h-4 w-4" />
              {t('scans.uploadNewScan')}
            </Button>
          </div>
        </div>

        {/* Patient Info Card */}
        <Card className="mb-6">
          <CardContent className="p-4">
            <div className="flex items-center gap-4">
              <div className="h-10 w-10 rounded-full bg-medical/10 flex items-center justify-center">
                <Brain className="h-5 w-5 text-medical" />
              </div>
              <div>
                <h2 className="font-semibold">
                  {patient.first_name} {patient.last_name}
                </h2>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Badge variant="outline" className="bg-medical/10 text-medical border-medical/20">
                    ID: {patient.id}
                  </Badge>
                  <span>•</span>
                  <span>{t('scans.totalScans')}: {scans.length}</span>
                  <span>•</span>
                  <span>{t('patients.dateOfBirth')}: {new Date(patient.date_of_birth).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Affichage conditionnel : Galerie ou Galerie d'images individuelles */}
        {showGallery && selectedScan ? (
          <IndividualImagesGallery
            segmentationId={selectedScan.id}
            patientName={`${patient.first_name} ${patient.last_name}`}
            onBack={() => {
              setShowGallery(false);
              setSelectedScan(null);
            }}
          />
        ) : (
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="gallery" className="flex items-center gap-2">
                <Grid className="h-4 w-4" />
                <span>Galerie</span>
              </TabsTrigger>
              <TabsTrigger value="comparison" className="flex items-center gap-2">
                <SplitSquareVertical className="h-4 w-4" />
                <span>Comparaison</span>
              </TabsTrigger>
              <TabsTrigger value="evolution" className="flex items-center gap-2">
                <BarChart className="h-4 w-4" />
                <span>Évolution</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="gallery" className="mt-6">
              <ScanGallery scans={scans} onSelectScan={handleScanSelect} />
            </TabsContent>

            <TabsContent value="comparison" className="mt-6">
              <ScanComparison
                scans={scans}
                patientName={`${patient.first_name} ${patient.last_name}`}
                patientId={patient.id}
                doctorName={patient.assigned_doctor?.user ?
                  `Dr. ${patient.assigned_doctor.user.first_name} ${patient.assigned_doctor.user.last_name}` :
                  'Non assigné'
                }
              />
            </TabsContent>

            <TabsContent value="evolution" className="mt-6">
              <TumorEvolutionChart
                scans={scans}
                patientName={`${patient.first_name} ${patient.last_name}`}
                patientId={patient.id}
                doctorName={patient.assigned_doctor?.user ?
                  `Dr. ${patient.assigned_doctor.user.first_name} ${patient.assigned_doctor.user.last_name}` :
                  'Non assigné'
                }
              />
            </TabsContent>
          </Tabs>
        )}

        {/* Message si aucune donnée */}
        {scans.length === 0 && !imagesLoading && !segmentationsLoading && (
          <Card className="mt-6">
            <CardContent className="pt-6">
              <div className="text-center py-8">
                <Brain className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">Aucune segmentation disponible</h3>
                <p className="text-muted-foreground">
                  Ce patient n'a pas encore de segmentations IA effectuées.
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
};

export default PatientExamHistory;
