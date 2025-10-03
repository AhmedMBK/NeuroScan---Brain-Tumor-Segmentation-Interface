import React from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import DoctorManagement from '@/components/admin/DoctorManagement';
import RoleBasedAccess from '@/components/common/RoleBasedAccess';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Info } from 'lucide-react';

const Doctors: React.FC = () => {
  const navigate = useNavigate();

  return (
    <RoleBasedAccess
      allowedRoles={['ADMIN', 'DOCTOR']}
      fallback={
        <DashboardLayout>
          <div className="p-6">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-destructive">Accès refusé</h1>
              <p className="text-muted-foreground mt-2">
                Vous n'avez pas les permissions nécessaires pour accéder à cette page.
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
            <h1 className="text-2xl font-bold tracking-tight">Liste des Médecins</h1>
            <p className="text-muted-foreground">
              Consulter les profils médicaux et leurs spécialités
            </p>
          </div>

          {/* Information sur le nouveau processus */}
          <Alert className="mb-6 border-blue-200 bg-blue-50">
            <Info className="h-4 w-4 text-blue-600" />
            <AlertDescription className="text-blue-800">
              <strong>Nouveau processus :</strong> Les médecins sont maintenant créés via la gestion des utilisateurs.
              Ils complètent automatiquement leur profil médical lors de leur première connexion.
            </AlertDescription>
          </Alert>

          {/* Contenu principal - Liste seulement */}
          <DoctorManagement
            onCreateDoctor={() => {}} // Fonction vide - plus de création ici
            onEditDoctor={() => {}} // Fonction vide - plus d'édition ici
            showCreateButton={false} // Masquer le bouton de création
          />
        </div>
      </DashboardLayout>
    </RoleBasedAccess>
  );
};

export default Doctors;
