import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import {
  Calendar,
  Users,
  FileText,
  Clock,
  TrendingUp,
  UserCheck,
  CalendarDays,
  Activity
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import { usePatients } from '@/hooks/usePatients';
import { useAppointments } from '@/hooks/api/useAppointments';
import { useDoctors } from '@/hooks/useDoctors';

const SecretaryDashboard: React.FC = () => {
  const { t } = useTranslation();
  const { userData } = useAuth();
  const { data: patientsData, isLoading: patientsLoading } = usePatients(1, 100);
  const { data: appointmentsData, isLoading: appointmentsLoading } = useAppointments();
  const { data: doctorsData, isLoading: doctorsLoading } = useDoctors();

  // Trouver les informations du médecin assigné
  const assignedDoctor = doctorsData?.doctors?.find((doctor: any) =>
    doctor.id === userData?.assigned_doctor_id
  );

  // Statistiques rapides
  const totalPatients = patientsData?.total || 0;
  const todayAppointments = appointmentsData?.filter((apt: any) => {
    const today = new Date().toDateString();
    return new Date(apt.appointment_date).toDateString() === today;
  }).length || 0;

  const upcomingAppointments = appointmentsData?.filter((apt: any) => {
    const now = new Date();
    const aptDate = new Date(apt.appointment_date);
    return aptDate > now;
  }).length || 0;

  return (
    <div className="space-y-6">
      {/* En-tête de bienvenue */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 p-6 rounded-lg">
        <div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-full bg-purple-100 dark:bg-purple-800 flex items-center justify-center">
            <UserCheck className="h-6 w-6 text-purple-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Bonjour, {userData?.first_name} {userData?.last_name}
            </h1>
            <p className="text-purple-600 dark:text-purple-400">
              Secrétaire médicale • Tableau de bord
            </p>
          </div>
        </div>
      </div>

      {/* Statistiques rapides */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Patients assignés</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {patientsLoading ? '...' : totalPatients}
            </div>
            <p className="text-xs text-muted-foreground">
              Patients de votre médecin
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">RDV aujourd'hui</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {appointmentsLoading ? '...' : todayAppointments}
            </div>
            <p className="text-xs text-muted-foreground">
              Rendez-vous programmés
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">RDV à venir</CardTitle>
            <CalendarDays className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {appointmentsLoading ? '...' : upcomingAppointments}
            </div>
            <p className="text-xs text-muted-foreground">
              Prochains rendez-vous
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Activité</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">
              <Badge variant="default">Actif</Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              Statut du système
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Actions rapides */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Actions rapides
            </CardTitle>
            <CardDescription>
              Tâches courantes pour la gestion des patients
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Button asChild variant="outline" className="h-auto p-4 flex flex-col items-center">
                <Link to="/patients/new">
                  <Users className="h-6 w-6 text-blue-600 mb-2" />
                  <div className="text-sm font-medium">Nouveau Patient</div>
                </Link>
              </Button>
              <Button asChild variant="outline" className="h-auto p-4 flex flex-col items-center">
                <Link to="/secretary/appointments">
                  <Calendar className="h-6 w-6 text-green-600 mb-2" />
                  <div className="text-sm font-medium">Planifier RDV</div>
                </Link>
              </Button>
              <Button asChild variant="outline" className="h-auto p-4 flex flex-col items-center">
                <Link to="/reports">
                  <FileText className="h-6 w-6 text-purple-600 mb-2" />
                  <div className="text-sm font-medium">Voir Rapports</div>
                </Link>
              </Button>
              <Button asChild variant="outline" className="h-auto p-4 flex flex-col items-center">
                <Link to="/secretary/appointments">
                  <Clock className="h-6 w-6 text-orange-600 mb-2" />
                  <div className="text-sm font-medium">Planning</div>
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Informations médecin
            </CardTitle>
            <CardDescription>
              Informations sur votre médecin assigné
            </CardDescription>
          </CardHeader>
          <CardContent>
            {userData?.assigned_doctor_id ? (
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-blue-100 dark:bg-blue-800 flex items-center justify-center">
                    <UserCheck className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    {doctorsLoading ? (
                      <div className="font-medium">Chargement...</div>
                    ) : assignedDoctor ? (
                      <>
                        <div className="font-medium">
                          Dr. {assignedDoctor.first_name} {assignedDoctor.last_name}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {assignedDoctor.email}
                        </div>
                        {assignedDoctor.office_location && (
                          <div className="text-sm text-muted-foreground">
                            📍 {assignedDoctor.office_location}
                          </div>
                        )}
                      </>
                    ) : (
                      <>
                        <div className="font-medium">Dr. Médecin Assigné</div>
                        <div className="text-sm text-muted-foreground">
                          ID: {userData.assigned_doctor_id}
                        </div>
                      </>
                    )}
                  </div>
                </div>
                <div className="pt-3 border-t">
                  <Badge variant="default" className="bg-green-100 text-green-800">
                    Assignée
                  </Badge>
                  {assignedDoctor?.is_active && (
                    <Badge variant="default" className="bg-blue-100 text-blue-800 ml-2">
                      Actif
                    </Badge>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-4">
                <div className="text-muted-foreground">
                  Aucun médecin assigné
                </div>
                <div className="text-sm text-muted-foreground mt-1">
                  Contactez l'administrateur
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SecretaryDashboard;
