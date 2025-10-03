import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { 
  ArrowLeft, 
  FileText, 
  User, 
  Calendar, 
  Brain,
  Download,
  Edit,
  CheckCircle,
  Clock
} from 'lucide-react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { useReport, useDownloadReport } from '@/hooks/api/useReports';
import RoleBasedAccess from '@/components/common/RoleBasedAccess';

const ReportView: React.FC = () => {
  const { reportId } = useParams<{ reportId: string }>();
  const navigate = useNavigate();

  const { data: report, isLoading, error } = useReport(reportId || '');
  const downloadReport = useDownloadReport();

  const handleDownload = () => {
    if (reportId) {
      downloadReport.mutate(reportId);
    }
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-medical mx-auto mb-4"></div>
              <p className="text-muted-foreground">Chargement du rapport...</p>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (error || !report) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="h-8 w-8 text-destructive mx-auto mb-4">⚠️</div>
              <p className="text-destructive">Erreur lors du chargement du rapport</p>
              <Button 
                variant="outline" 
                onClick={() => navigate('/reports')}
                className="mt-4"
              >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Retour aux rapports
              </Button>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6 max-w-4xl mx-auto">
        {/* En-tête */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <Button 
              variant="outline" 
              onClick={() => navigate('/reports')}
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Retour
            </Button>
            <div>
              <h1 className="text-2xl font-bold">Rapport de Segmentation</h1>
              <p className="text-muted-foreground">
                Rapport #{report.id.slice(0, 8)}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Badge variant={report.is_final ? 'default' : 'secondary'}>
              {report.is_final ? (
                <>
                  <CheckCircle className="mr-1 h-3 w-3" />
                  Final
                </>
              ) : (
                <>
                  <Clock className="mr-1 h-3 w-3" />
                  Brouillon
                </>
              )}
            </Badge>
            
            <RoleBasedAccess requiredPermissions={['can_edit_reports']}>
              <Button variant="outline" size="sm">
                <Edit className="mr-2 h-4 w-4" />
                Modifier
              </Button>
            </RoleBasedAccess>
            
            <RoleBasedAccess requiredPermissions={['can_export_data']}>
              <Button
                variant="outline"
                size="sm"
                disabled={!report.is_final || downloadReport.isPending}
                onClick={handleDownload}
              >
                <Download className="mr-2 h-4 w-4" />
                {downloadReport.isPending ? 'Téléchargement...' : 'Exporter'}
              </Button>
            </RoleBasedAccess>
          </div>
        </div>

        {/* Informations du rapport */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <User className="h-4 w-4" />
                Patient
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-lg font-semibold">
                {report.segmentation?.patient ? 
                  `${report.segmentation.patient.first_name} ${report.segmentation.patient.last_name}` :
                  'Patient non spécifié'
                }
              </div>
              {report.segmentation?.patient?.email && (
                <div className="text-sm text-muted-foreground">
                  {report.segmentation.patient.email}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <User className="h-4 w-4" />
                Médecin
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-lg font-semibold">
                {report.doctor?.user ? 
                  `Dr. ${report.doctor.user.first_name} ${report.doctor.user.last_name}` :
                  'Médecin non spécifié'
                }
              </div>
              {report.doctor?.user?.email && (
                <div className="text-sm text-muted-foreground">
                  {report.doctor.user.email}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Date de création
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-lg font-semibold">
                {format(new Date(report.created_at), 'dd MMMM yyyy', { locale: fr })}
              </div>
              <div className="text-sm text-muted-foreground">
                {format(new Date(report.created_at), 'HH:mm')}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Informations de segmentation */}
        {report.segmentation && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                Segmentation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <div className="text-sm font-medium text-muted-foreground">ID de segmentation</div>
                  <div className="font-mono text-sm">{report.segmentation.id}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-muted-foreground">Statut</div>
                  <Badge variant="outline">{report.segmentation.status}</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Contenu du rapport */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Contenu du rapport
            </CardTitle>
            <CardDescription>
              Analyse détaillée de la segmentation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm max-w-none">
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {report.report_content || 'Aucun contenu disponible'}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Métadonnées */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-sm">Métadonnées</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <div className="font-medium text-muted-foreground">ID du rapport</div>
                <div className="font-mono">{report.id}</div>
              </div>
              <div>
                <div className="font-medium text-muted-foreground">Dernière modification</div>
                <div>{format(new Date(report.updated_at), 'dd/MM/yyyy HH:mm')}</div>
              </div>
              {report.template_used && (
                <div>
                  <div className="font-medium text-muted-foreground">Modèle utilisé</div>
                  <div>{report.template_used}</div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default ReportView;
