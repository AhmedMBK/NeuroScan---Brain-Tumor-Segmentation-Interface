import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';
import { 
  FileText, 
  Download, 
  Eye,
  Filter,
  Calendar,
  BarChart3,
  PieChart,
  TrendingUp,
  Users,
  Brain,
  Activity
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useReports, useDownloadReport } from '@/hooks/api/useReports';
import RoleBasedAccess from '@/components/common/RoleBasedAccess';

interface ReportsManagementProps {
  onViewReport: (reportId: string) => void;
  onGenerateReport: () => void;
}

const ReportsManagement: React.FC<ReportsManagementProps> = ({ 
  onViewReport, 
  onGenerateReport 
}) => {
  const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [selectedPeriod, setSelectedPeriod] = useState<string>('ALL');

  // Hooks API
  const { data: reports = [], isLoading, error } = useReports();
  const downloadReport = useDownloadReport();

  const handleDownload = (reportId: string) => {
    downloadReport.mutate(reportId);
  };

  // Filtrage des rapports (conforme à SegmentationReport)
  const filteredReports = reports.filter((report: any) => {
    const matchesSearch =
      report.report_content?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.segmentation_id?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesType = selectedType === 'ALL' ||
      (selectedType === 'FINAL' && report.is_final) ||
      (selectedType === 'DRAFT' && !report.is_final);

    const matchesPeriod = selectedPeriod === 'ALL' ||
      (selectedPeriod === 'WEEK' && isWithinLastWeek(report.created_at)) ||
      (selectedPeriod === 'MONTH' && isWithinLastMonth(report.created_at)) ||
      (selectedPeriod === 'YEAR' && isWithinLastYear(report.created_at));

    return matchesSearch && matchesType && matchesPeriod;
  });

  // Fonctions utilitaires pour les périodes
  const isWithinLastWeek = (date: string) => {
    const reportDate = new Date(date);
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    return reportDate >= weekAgo;
  };

  const isWithinLastMonth = (date: string) => {
    const reportDate = new Date(date);
    const monthAgo = new Date();
    monthAgo.setMonth(monthAgo.getMonth() - 1);
    return reportDate >= monthAgo;
  };

  const isWithinLastYear = (date: string) => {
    const reportDate = new Date(date);
    const yearAgo = new Date();
    yearAgo.setFullYear(yearAgo.getFullYear() - 1);
    return reportDate >= yearAgo;
  };



  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Gestion des Rapports
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-medical mx-auto mb-4"></div>
              <p className="text-muted-foreground">Chargement des rapports...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Gestion des Rapports
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="h-8 w-8 text-destructive mx-auto mb-4">⚠️</div>
              <p className="text-destructive">Erreur lors du chargement des rapports</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Gestion des Rapports
            </CardTitle>
            <CardDescription>
              Générer, consulter et exporter les rapports d'analyse et de segmentation
            </CardDescription>
          </div>
          <RoleBasedAccess requiredPermissions={['can_view_reports']}>
            <Button onClick={onGenerateReport}>
              <BarChart3 className="mr-2 h-4 w-4" />
              Générer Rapport
            </Button>
          </RoleBasedAccess>
        </div>
      </CardHeader>
      <CardContent>
        {/* Filtres et recherche */}
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1 max-w-sm">
            <Input
              placeholder="Rechercher un rapport..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <Select value={selectedType} onValueChange={setSelectedType}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Statut du rapport" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">Tous les statuts</SelectItem>
              <SelectItem value="FINAL">Rapports finaux</SelectItem>
              <SelectItem value="DRAFT">Brouillons</SelectItem>
            </SelectContent>
          </Select>

          <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Période" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">Toutes</SelectItem>
              <SelectItem value="WEEK">7 derniers jours</SelectItem>
              <SelectItem value="MONTH">30 derniers jours</SelectItem>
              <SelectItem value="YEAR">Cette année</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Statistiques rapides */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{reports.length}</div>
            <div className="text-sm text-blue-600">Total Rapports</div>
          </div>
          <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {reports.filter((r: any) => r.is_final).length}
            </div>
            <div className="text-sm text-green-600">Rapports finaux</div>
          </div>
          <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">
              {reports.filter((r: any) => !r.is_final).length}
            </div>
            <div className="text-sm text-orange-600">Brouillons</div>
          </div>
          <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {reports.filter((r: any) => isWithinLastWeek(r.created_at)).length}
            </div>
            <div className="text-sm text-purple-600">Cette semaine</div>
          </div>
        </div>

        {/* Table des rapports */}
        <div className="border rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Rapport</TableHead>
                <TableHead>Patient</TableHead>
                <TableHead>Segmentation</TableHead>
                <TableHead>Statut</TableHead>
                <TableHead>Médecin</TableHead>
                <TableHead>Date</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredReports.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-8">
                    <div className="text-muted-foreground">
                      {searchTerm || selectedType !== 'ALL' || selectedPeriod !== 'ALL'
                        ? 'Aucun rapport trouvé avec ces critères'
                        : 'Aucun rapport de segmentation créé'
                      }
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                filteredReports.map((report: any) => (
                  <TableRow key={report.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <FileText className="h-4 w-4 text-medical" />
                        <div>
                          <div className="font-medium">
                            Rapport #{report.id.slice(0, 8)}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {report.report_content?.slice(0, 60)}...
                          </div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {report.segmentation?.patient ?
                          `${report.segmentation.patient.first_name} ${report.segmentation.patient.last_name}` :
                          'Patient non spécifié'
                        }
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm text-muted-foreground">
                        {report.segmentation_id.slice(0, 8)}...
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={report.is_final ? 'default' : 'secondary'}>
                        {report.is_final ? 'Final' : 'Brouillon'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {report.doctor?.user ?
                          `Dr. ${report.doctor.user.first_name} ${report.doctor.user.last_name}` :
                          'Médecin non spécifié'
                        }
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {format(new Date(report.created_at), 'dd/MM/yyyy HH:mm')}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center gap-2 justify-end">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onViewReport(report.id)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <RoleBasedAccess requiredPermissions={['can_export_data']}>
                          <Button
                            variant="ghost"
                            size="sm"
                            disabled={!report.is_final || downloadReport.isPending}
                            onClick={() => handleDownload(report.id)}
                          >
                            <Download className="h-4 w-4" />
                          </Button>
                        </RoleBasedAccess>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
};

export default ReportsManagement;
