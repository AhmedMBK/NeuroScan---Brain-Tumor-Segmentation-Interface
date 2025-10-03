import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ArrowLeft } from 'lucide-react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import PatientForm from '@/components/forms/PatientForm';
import { Button } from '@/components/ui/button';
import { useCreatePatient } from '@/hooks/usePatients';
import RoleBasedAccess from '@/components/common/RoleBasedAccess';

const PatientCreate: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const createPatientMutation = useCreatePatient();

  const handleSubmit = async (data: any) => {
    try {
      const newPatient = await createPatientMutation.mutateAsync(data);
      // Rediriger vers la page du patient créé
      navigate(`/patients/${newPatient.id}`);
    } catch (error) {
      // L'erreur est déjà gérée par le hook
      console.error('Erreur lors de la création:', error);
    }
  };

  const handleCancel = () => {
    navigate('/patients');
  };

  return (
    <RoleBasedAccess 
      requiredPermissions={['can_create_patients']}
      fallback={
        <DashboardLayout>
          <div className="p-6">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-destructive">Accès refusé</h1>
              <p className="text-muted-foreground mt-2">
                Vous n'avez pas les permissions nécessaires pour créer des patients.
              </p>
              <Button 
                variant="outline" 
                onClick={() => navigate('/patients')}
                className="mt-4"
              >
                Retour à la liste
              </Button>
            </div>
          </div>
        </DashboardLayout>
      }
    >
      <DashboardLayout>
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center gap-4 mb-6">
            <Button 
              variant="outline" 
              size="icon" 
              onClick={() => navigate('/patients')}
              className="h-8 w-8"
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">{t('patients.addPatient')}</h1>
              <p className="text-muted-foreground">
                {t('patients.createPatientDescription')}
              </p>
            </div>
          </div>

          {/* Formulaire */}
          <PatientForm
            mode="create"
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            isLoading={createPatientMutation.isPending}
          />
        </div>
      </DashboardLayout>
    </RoleBasedAccess>
  );
};

export default PatientCreate;
