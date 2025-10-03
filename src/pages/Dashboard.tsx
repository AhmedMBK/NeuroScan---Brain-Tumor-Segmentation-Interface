import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import {
  Users,
  FileText,
  PlusCircle,
  Upload,
  Clock,
  CheckCircle,
  ArrowRight,
  Brain,
  Activity
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { usePatientsStats } from '@/hooks/usePatients';
import { useSegmentationStats, useRecentSegmentations } from '@/hooks/useSegmentation';
import RoleBasedAccess from '@/components/common/RoleBasedAccess';
import { usePermissions } from '@/utils/permissions';
import QuickNavigation from '@/components/common/QuickNavigation';
import SecretaryDashboard from '@/components/secretary/SecretaryDashboard';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  description?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, description }) => (
  <Card>
    <CardHeader className="flex flex-row items-center justify-between pb-2">
      <CardTitle className="text-sm font-medium">{title}</CardTitle>
      <div className="h-8 w-8 rounded-full bg-medical/10 flex items-center justify-center">
        {icon}
      </div>
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold">{value}</div>
      {description && (
        <p className="text-xs text-muted-foreground">{description}</p>
      )}
    </CardContent>
  </Card>
);

interface ActionCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  to: string;
}

const ActionCard: React.FC<ActionCardProps> = ({ title, description, icon, to }) => (
  <Card className="overflow-hidden">
    <CardHeader className="pb-2">
      <div className="h-8 w-8 rounded-full bg-medical/10 flex items-center justify-center">
        {icon}
      </div>
      <CardTitle className="text-lg mt-2">{title}</CardTitle>
      <CardDescription>{description}</CardDescription>
    </CardHeader>
    <CardFooter className="pt-2">
      <Button asChild variant="ghost" className="p-0 h-auto font-normal text-medical">
        <Link to={to} className="flex items-center">
          <span>View</span>
          <ArrowRight className="ml-1 h-4 w-4" />
        </Link>
      </Button>
    </CardFooter>
  </Card>
);

const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  const { userData } = useAuth();
  const permissions = usePermissions(userData);
  const displayName = userData?.displayName || '';

  // ✅ AJOUTÉ : Dashboard spécifique pour les secrétaires
  if (userData?.role === 'SECRETARY') {
    return (
      <DashboardLayout>
        <div className="p-6">
          <SecretaryDashboard />
        </div>
      </DashboardLayout>
    );
  }

  // Récupération des vraies données depuis l'API
  const { data: patientsStats, isLoading: loadingPatients } = usePatientsStats();
  const { data: segmentationStats, isLoading: loadingSegmentations } = useSegmentationStats();
  const { data: recentSegmentations, isLoading: loadingRecent } = useRecentSegmentations(5);

  // Données par défaut en cas de chargement
  const stats = {
    patientCount: patientsStats?.total_patients || 0,
    segmentationCount: segmentationStats?.segmentation_counts?.total || 0,
    pendingSegmentations: segmentationStats?.segmentation_counts?.processing || 0,
    completedSegmentations: segmentationStats?.segmentation_counts?.completed || 0,
    validatedSegmentations: segmentationStats?.segmentation_counts?.validated || 0,
  };

  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">
            {t('dashboard.welcome')}, {displayName}
          </h1>
          <p className="text-muted-foreground">
            {new Date().toLocaleDateString(undefined, {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          <StatCard
            title="Patients"
            value={loadingPatients ? "..." : stats.patientCount}
            icon={<Users className="h-4 w-4 text-medical" />}
            description="Total des patients enregistrés"
          />
          <StatCard
            title="Segmentations IA"
            value={loadingSegmentations ? "..." : stats.segmentationCount}
            icon={<Brain className="h-4 w-4 text-medical" />}
            description="Analyses par modèle U-Net"
          />
          <StatCard
            title="En cours"
            value={loadingSegmentations ? "..." : stats.pendingSegmentations}
            icon={<Clock className="h-4 w-4 text-orange-500" />}
            description="Segmentations en traitement"
          />
          <StatCard
            title="Terminées"
            value={loadingSegmentations ? "..." : stats.completedSegmentations}
            icon={<CheckCircle className="h-4 w-4 text-green-500" />}
            description="Segmentations complétées"
          />
          <StatCard
            title="Validées"
            value={loadingSegmentations ? "..." : stats.validatedSegmentations}
            icon={<Activity className="h-4 w-4 text-blue-500" />}
            description="Validées par médecins"
          />
        </div>

        <h2 className="text-xl font-semibold mt-10 mb-4">{t('dashboard.quickActions')}</h2>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <RoleBasedAccess requiredPermissions={['can_view_patients']}>
            <ActionCard
              title={t('dashboard.viewAllPatients')}
              description="View and manage all patient records"
              icon={<Users className="h-4 w-4 text-medical" />}
              to="/patients"
            />
          </RoleBasedAccess>

          <RoleBasedAccess requiredPermissions={['can_create_patients']}>
            <ActionCard
              title={t('dashboard.addNewPatient')}
              description="Register a new patient in the system"
              icon={<PlusCircle className="h-4 w-4 text-medical" />}
              to="/patients/new"
            />
          </RoleBasedAccess>

          <RoleBasedAccess requiredPermissions={['can_create_segmentations']}>
            <ActionCard
              title={t('dashboard.uploadNewScan')}
              description="Upload and analyze a new MRI scan"
              icon={<Upload className="h-4 w-4 text-medical" />}
              to="/scans/new"
            />
          </RoleBasedAccess>

          <RoleBasedAccess allowedRoles={['ADMIN']}>
            <ActionCard
              title={t('dashboard.manageUsers')}
              description="Manage user accounts and permissions"
              icon={<Users className="h-4 w-4 text-medical" />}
              to="/users"
            />
          </RoleBasedAccess>
        </div>

        {/* Navigation rapide */}
        <div className="mt-10 mb-6">
          <QuickNavigation currentPage="dashboard" />
        </div>



        <h2 className="text-xl font-semibold mt-10 mb-4">Segmentations Récentes</h2>

        <Card>
          <CardHeader>
            <CardTitle>Analyses IA Récentes</CardTitle>
            <CardDescription>
              Dernières segmentations de tumeurs cérébrales par modèle U-Net
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loadingRecent ? (
              <div className="text-center py-6 text-muted-foreground">
                <p>Chargement des segmentations récentes...</p>
              </div>
            ) : !recentSegmentations?.items || recentSegmentations.items.length === 0 ? (
              <div className="text-center py-6 text-muted-foreground">
                <p>Aucune segmentation récente à afficher</p>
                <p className="text-sm mt-2">Uploadez des images IRM pour commencer l'analyse</p>
              </div>
            ) : (
              <div className="space-y-3">
                {recentSegmentations.items.map((segmentation: any) => (
                  <div key={segmentation.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full ${
                        segmentation.status === 'COMPLETED' ? 'bg-green-500' :
                        segmentation.status === 'PROCESSING' ? 'bg-orange-500' :
                        segmentation.status === 'VALIDATED' ? 'bg-blue-500' : 'bg-red-500'
                      }`} />
                      <div>
                        <p className="font-medium">Patient {segmentation.patient_id}</p>
                        <p className="text-sm text-muted-foreground">
                          {segmentation.segmentation_results?.total_tumor_volume_cm3 ?
                            `Volume: ${segmentation.segmentation_results.total_tumor_volume_cm3.toFixed(1)} cm³` :
                            segmentation.segmentation_results?.tumor_analysis?.total_volume_cm3 ?
                            `Volume: ${segmentation.segmentation_results.tumor_analysis.total_volume_cm3.toFixed(1)} cm³` :
                            'En cours d\'analyse...'
                          }
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">
                        {segmentation.status === 'COMPLETED' ? 'Terminé' :
                         segmentation.status === 'PROCESSING' ? 'En cours' :
                         segmentation.status === 'VALIDATED' ? 'Validé' : 'Échec'}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(segmentation.started_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button variant="outline" asChild>
              <Link to="/patients">Voir toutes les segmentations</Link>
            </Button>
            <Button asChild>
              <Link to="/patients">Nouvelle segmentation</Link>
            </Button>
          </CardFooter>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default Dashboard;
