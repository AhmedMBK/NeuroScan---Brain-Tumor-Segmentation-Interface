import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import ReportsManagement from '@/components/reports/ReportsManagement';
import RoleBasedAccess from '@/components/common/RoleBasedAccess';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { useCreateReport } from '@/hooks/api/useReports';
import { usePatientsForSelect } from '@/hooks/usePatients';
import { useSegmentationsForSelect } from '@/hooks/api/useSegmentations';

const Reports: React.FC = () => {
  const navigate = useNavigate();
  const [isGenerateDialogOpen, setIsGenerateDialogOpen] = useState(false);

  // États pour le formulaire de génération (conforme à SegmentationReport)
  const [selectedSegmentationId, setSelectedSegmentationId] = useState('');
  const [reportContent, setReportContent] = useState('');
  const [findings, setFindings] = useState('');
  const [recommendations, setRecommendations] = useState('');
  const [selectedPatientId, setSelectedPatientId] = useState<string>('');
  const [isFinal, setIsFinal] = useState(false);

  // Hooks API
  const createReportMutation = useCreateReport();
  const { data: patients = [], isLoading: patientsLoading } = usePatientsForSelect();
  const { data: segmentations = [], isLoading: segmentationsLoading } = useSegmentationsForSelect(selectedPatientId);

  // Gestion de la génération de rapport
  const handleGenerateReport = () => {
    setIsGenerateDialogOpen(true);
  };

  // Gestion de la visualisation de rapport
  const handleViewReport = (reportId: string) => {
    // Naviguer vers la page de visualisation du rapport
    navigate(`/reports/${reportId}`);
  };

  // Soumission du formulaire de génération
  const handleSubmitGeneration = async () => {
    if (!selectedSegmentationId || !reportContent) {
      return;
    }

    try {
      const reportData = {
        segmentation_id: selectedSegmentationId,
        report_content: reportContent,
        findings: findings ? { content: findings } : undefined,
        recommendations: recommendations ? { content: recommendations } : undefined,
        is_final: isFinal
      };

      await createReportMutation.mutateAsync(reportData);
      handleCancelGeneration();
    } catch (error) {
      console.error('Erreur lors de la génération du rapport:', error);
    }
  };

  // Annulation de la génération
  const handleCancelGeneration = () => {
    setIsGenerateDialogOpen(false);
    setSelectedSegmentationId('');
    setReportContent('');
    setFindings('');
    setRecommendations('');
    setSelectedPatientId('');
    setIsFinal(false);
  };

  return (
    <RoleBasedAccess 
      requiredPermissions={['can_view_reports']}
      fallback={
        <DashboardLayout>
          <div className="p-6">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-destructive">Accès refusé</h1>
              <p className="text-muted-foreground mt-2">
                Vous n'avez pas les permissions nécessaires pour accéder aux rapports.
              </p>
              <Button 
                variant="outline" 
                onClick={() => navigate('/dashboard')}
                className="mt-4"
              >
                Retour au tableau de bord
              </Button>
            </div>
          </div>
        </DashboardLayout>
      }
    >
      <DashboardLayout>
        <div className="p-6">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold tracking-tight">Rapports & Analyses</h1>
            <p className="text-muted-foreground">
              Générer et consulter les rapports d'analyse, de segmentation et de suivi des traitements
            </p>
          </div>

          {/* Contenu principal */}
          <ReportsManagement
            onViewReport={handleViewReport}
            onGenerateReport={handleGenerateReport}
          />

          {/* Dialog pour génération de rapport */}
          <Dialog open={isGenerateDialogOpen} onOpenChange={setIsGenerateDialogOpen}>
            <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
              <DialogHeader className="flex-shrink-0">
                <DialogTitle>Créer un Rapport de Segmentation</DialogTitle>
                <DialogDescription>
                  Créer un rapport d'analyse pour une segmentation IA spécifique
                </DialogDescription>
              </DialogHeader>

              <div className="flex-1 overflow-y-auto px-1">
                <div className="space-y-6 py-4">
                {/* Sélection du patient */}
                <div className="space-y-2">
                  <Label htmlFor="patientSelect">Patient *</Label>
                  <Select value={selectedPatientId} onValueChange={setSelectedPatientId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Sélectionner un patient" />
                    </SelectTrigger>
                    <SelectContent>
                      {patientsLoading ? (
                        <SelectItem value="loading" disabled>Chargement des patients...</SelectItem>
                      ) : patients.length === 0 ? (
                        <SelectItem value="empty" disabled>Aucun patient disponible</SelectItem>
                      ) : (
                        patients.map((patient: any) => (
                          <SelectItem key={patient.value} value={patient.value}>
                            {patient.label}
                            {patient.email && <span className="text-muted-foreground ml-2">({patient.email})</span>}
                          </SelectItem>
                        ))
                      )}
                    </SelectContent>
                  </Select>
                </div>

                {/* Sélection de la segmentation */}
                <div className="space-y-2">
                  <Label htmlFor="segmentationSelect">Segmentation *</Label>
                  <Select
                    value={selectedSegmentationId}
                    onValueChange={setSelectedSegmentationId}
                    disabled={!selectedPatientId}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={
                        !selectedPatientId
                          ? "Sélectionner d'abord un patient"
                          : "Sélectionner une segmentation"
                      } />
                    </SelectTrigger>
                    <SelectContent>
                      {segmentationsLoading ? (
                        <SelectItem value="loading" disabled>Chargement des segmentations...</SelectItem>
                      ) : segmentations.length === 0 ? (
                        <SelectItem value="empty" disabled>
                          {selectedPatientId ? "Aucune segmentation terminée pour ce patient" : "Sélectionner un patient"}
                        </SelectItem>
                      ) : (
                        segmentations.map((segmentation: any) => (
                          <SelectItem key={segmentation.value} value={segmentation.value}>
                            {segmentation.label}
                            {segmentation.completed_at && (
                              <span className="text-muted-foreground ml-2">
                                ({new Date(segmentation.completed_at).toLocaleDateString()})
                              </span>
                            )}
                          </SelectItem>
                        ))
                      )}
                    </SelectContent>
                  </Select>
                </div>

                {/* Contenu du rapport */}
                <div className="space-y-2">
                  <Label htmlFor="reportContent">Contenu du rapport *</Label>
                  <Textarea
                    id="reportContent"
                    placeholder="Contenu principal du rapport d'analyse..."
                    value={reportContent}
                    onChange={(e) => setReportContent(e.target.value)}
                    className="resize-none h-40"
                  />
                </div>

                {/* Observations cliniques */}
                <div className="space-y-2">
                  <Label htmlFor="findings">Observations cliniques</Label>
                  <Textarea
                    id="findings"
                    placeholder="Observations et résultats cliniques détaillés..."
                    value={findings}
                    onChange={(e) => setFindings(e.target.value)}
                    className="resize-none h-32"
                  />
                </div>

                {/* Recommandations */}
                <div className="space-y-2">
                  <Label htmlFor="recommendations">Recommandations</Label>
                  <Textarea
                    id="recommendations"
                    placeholder="Recommandations médicales et prochaines étapes..."
                    value={recommendations}
                    onChange={(e) => setRecommendations(e.target.value)}
                    className="resize-none h-32"
                  />
                </div>

                {/* Statut final */}
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="isFinal"
                    checked={isFinal}
                    onChange={(e) => setIsFinal(e.target.checked)}
                    className="rounded border-gray-300"
                  />
                  <Label htmlFor="isFinal">Marquer comme rapport final</Label>
                </div>

                {/* Information d'aide */}
                {selectedSegmentationId && (
                  <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                    <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
                      📋 Rapport de Segmentation IA
                    </h4>
                    <p className="text-sm text-blue-700 dark:text-blue-300">
                      Ce rapport analysera les résultats de la segmentation sélectionnée avec des observations cliniques détaillées et des recommandations médicales.
                    </p>
                  </div>
                )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-end space-x-4 pt-4 border-t flex-shrink-0">
                <Button
                  variant="outline"
                  onClick={handleCancelGeneration}
                  disabled={createReportMutation.isPending}
                >
                  Annuler
                </Button>
                <Button
                  onClick={handleSubmitGeneration}
                  disabled={!selectedSegmentationId || !reportContent || createReportMutation.isPending}
                >
                  {createReportMutation.isPending ? 'Création...' : 'Créer Rapport'}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </DashboardLayout>
    </RoleBasedAccess>
  );
};

export default Reports;
