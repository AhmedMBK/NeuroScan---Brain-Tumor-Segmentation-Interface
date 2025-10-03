import React from 'react';
import { useTranslation } from 'react-i18next';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import AppointmentScheduling from '@/components/secretary/AppointmentScheduling';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Calendar, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

const SecretaryAppointmentsPage: React.FC = () => {
  const { t } = useTranslation();
  const { userData } = useAuth();

  // Vérifier que l'utilisateur est une secrétaire
  if (userData?.role !== 'SECRETARY') {
    return (
      <DashboardLayout>
        <div className="p-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Planning des Rendez-vous
              </CardTitle>
              <CardDescription>
                Accès réservé aux secrétaires
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  Vous n'avez pas les permissions nécessaires pour accéder à cette page. 
                  Cette interface est réservée aux secrétaires médicales.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight">
            Planning des Rendez-vous
          </h1>
          <p className="text-muted-foreground">
            Gérez les rendez-vous de votre médecin
          </p>
        </div>
        
        <AppointmentScheduling />
      </div>
    </DashboardLayout>
  );
};

export default SecretaryAppointmentsPage;
