import React from 'react';
import { useTranslation } from 'react-i18next';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import SecretaryManagement from '@/components/doctor/SecretaryManagement';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

const SecretaryManagementPage: React.FC = () => {
  const { t } = useTranslation();
  const { userData } = useAuth();

  // Vérifier que l'utilisateur est un médecin
  if (userData?.role !== 'DOCTOR') {
    return (
      <DashboardLayout>
        <div className="p-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Gestion des Secrétaires
              </CardTitle>
              <CardDescription>
                Accès réservé aux médecins
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  Vous n'avez pas les permissions nécessaires pour accéder à cette page. 
                  Seuls les médecins peuvent gérer leurs secrétaires.
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
            Gestion des Secrétaires
          </h1>
          <p className="text-muted-foreground">
            Gérez les secrétaires assignées à votre cabinet médical
          </p>
        </div>
        
        <SecretaryManagement />
      </div>
    </DashboardLayout>
  );
};

export default SecretaryManagementPage;
