import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import PatientForm from '@/components/forms/PatientForm';
import { Button } from '@/components/ui/button';
import { usePatient, useUpdatePatient } from '@/hooks/usePatients';
import RoleBasedAccess from '@/components/common/RoleBasedAccess';

const PatientEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const updatePatientMutation = useUpdatePatient();
  
  // Récupérer les données du patient
  const { data: patient, isLoading: patientLoading, error } = usePatient(id || '');

  const handleSubmit = async (data: any) => {
    if (!id) return;
    
    try {
      await updatePatientMutation.mutateAsync({ id, data });
      // Rediriger vers la page du patient
      navigate(`/patients/${id}`);
    } catch (error) {
      // L'erreur est déjà gérée par le hook
      console.error('Erreur lors de la modification:', error);
    }
  };

  const handleCancel = () => {
    navigate(`/patients/${id}`);
  };

  if (patientLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-medical"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (error || !patient) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="text-center">
            <h2 className="text-2xl font-bold">Patient non trouvé</h2>
            <p className="text-muted-foreground mt-2">
              Le patient demandé n'existe pas ou vous n'avez pas les permissions pour le voir.
            </p>
            <Button 
              variant="outline" 
              onClick={() => navigate('/patients')}
              className="mt-4"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Retour à la liste
            </Button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <RoleBasedAccess 
      requiredPermissions={['can_edit_patients']}
      fallback={
        <DashboardLayout>
          <div className="p-6">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-destructive">Accès refusé</h1>
              <p className="text-muted-foreground mt-2">
                Vous n'avez pas les permissions nécessaires pour modifier ce patient.
              </p>
              <Button 
                variant="outline" 
                onClick={() => navigate(`/patients/${id}`)}
                className="mt-4"
              >
                Retour au patient
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
              onClick={() => navigate(`/patients/${id}`)}
              className="h-8 w-8"
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Modifier Patient</h1>
              <p className="text-muted-foreground">
                Modifier les informations de {patient.first_name} {patient.last_name}
              </p>
            </div>
          </div>

          {/* Formulaire */}
          <PatientForm
            mode="edit"
            initialData={patient}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            isLoading={updatePatientMutation.isPending}
          />
        </div>
      </DashboardLayout>
    </RoleBasedAccess>
  );
};

export default PatientEdit;
