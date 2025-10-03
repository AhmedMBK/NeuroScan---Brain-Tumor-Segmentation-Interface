import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import ImageUploadForm from '@/components/medical/ImageUploadForm';
import { Button } from '@/components/ui/button';
import { useImageUpload } from '@/hooks/api/useImageUpload';
import RoleBasedAccess from '@/components/common/RoleBasedAccess';
import { usePatient } from '@/hooks/usePatients';

const ImageUpload: React.FC = () => {
  const navigate = useNavigate();
  const { patientId } = useParams<{ patientId: string }>();
  const uploadMutation = useImageUpload();
  
  // Récupérer les infos du patient pour affichage
  const { data: patient, isLoading: patientLoading } = usePatient(patientId || '');

  const handleUploadComplete = (imageIds: string[]) => {
    // Rediriger vers la page du patient avec onglet images
    navigate(`/patients/${patientId}?tab=images`);
  };

  const handleCancel = () => {
    navigate(`/patients/${patientId}`);
  };

  const handleSubmit = async (formData: any) => {
    if (!patientId) return;

    // Transformer les données du formulaire pour l'API
    const uploadData = {
      patient_id: patientId,
      acquisition_date: formData.acquisition_date,
      notes: formData.notes,
      files: formData.modalityFiles
        .filter((item: any) => item.file)
        .map((item: any) => ({
          modality: item.modality,
          file: item.file,
        })),
    };

    try {
      const result = await uploadMutation.mutateAsync(uploadData);
      handleUploadComplete(result.images.map((img: any) => img.id));
    } catch (error) {
      // L'erreur est déjà gérée par le hook
      console.error('Erreur lors de l\'upload:', error);
    }
  };

  if (!patientId) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-destructive">Erreur</h1>
            <p className="text-muted-foreground mt-2">
              ID patient manquant dans l'URL.
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
    );
  }

  return (
    <RoleBasedAccess 
      requiredPermissions={['can_create_segmentations']}
      fallback={
        <DashboardLayout>
          <div className="p-6">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-destructive">Accès refusé</h1>
              <p className="text-muted-foreground mt-2">
                Vous n'avez pas les permissions nécessaires pour uploader des images.
              </p>
              <Button 
                variant="outline" 
                onClick={() => navigate(`/patients/${patientId}`)}
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
              onClick={() => navigate(`/patients/${patientId}`)}
              className="h-8 w-8"
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Upload Images Médicales</h1>
              {patientLoading ? (
                <p className="text-muted-foreground">Chargement...</p>
              ) : patient ? (
                <p className="text-muted-foreground">
                  Patient: {patient.first_name} {patient.last_name}
                </p>
              ) : (
                <p className="text-muted-foreground">
                  ID Patient: {patientId}
                </p>
              )}
            </div>
          </div>

          {/* Formulaire d'upload */}
          <ImageUploadForm
            patientId={patientId}
            onUploadComplete={handleUploadComplete}
            onCancel={handleCancel}
          />
        </div>
      </DashboardLayout>
    </RoleBasedAccess>
  );
};

export default ImageUpload;
