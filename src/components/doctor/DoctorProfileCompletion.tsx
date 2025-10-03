import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, UserCheck, Stethoscope } from 'lucide-react';
import { useCompleteDoctorProfile } from '@/hooks/api/useDoctorProfile';

// Schéma de validation
const doctorProfileSchema = z.object({
  bio: z.string().optional(),
  office_location: z.string().optional(),
});

type DoctorProfileFormData = z.infer<typeof doctorProfileSchema>;

interface DoctorProfileCompletionProps {
  onProfileCompleted: () => void;
}



const DoctorProfileCompletion: React.FC<DoctorProfileCompletionProps> = ({
  onProfileCompleted,
}) => {
  const completeDoctorProfileMutation = useCompleteDoctorProfile();

  const form = useForm<DoctorProfileFormData>({
    resolver: zodResolver(doctorProfileSchema),
    defaultValues: {
      bio: '',
      office_location: '',
    },
  });

  const onSubmit = async (data: DoctorProfileFormData) => {
    try {
      await completeDoctorProfileMutation.mutateAsync(data);

      // Appeler la fonction de callback
      onProfileCompleted();

    } catch (error) {
      console.error('Erreur lors de la complétion du profil:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 p-3 bg-blue-100 rounded-full w-fit">
            <Stethoscope className="h-8 w-8 text-blue-600" />
          </div>
          <CardTitle className="text-2xl font-bold text-gray-900">
            Compléter votre profil médecin
          </CardTitle>
          <CardDescription className="text-gray-600">
            Complétez votre profil médecin avec vos informations professionnelles
          </CardDescription>
        </CardHeader>

        <CardContent>
          <Alert className="mb-6 border-blue-200 bg-blue-50">
            <UserCheck className="h-4 w-4 text-blue-600" />
            <AlertDescription className="text-blue-800">
              Votre profil médecin vous permettra d'accéder à toutes les fonctionnalités de CereBloom.
            </AlertDescription>
          </Alert>

          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="office_location">Localisation du bureau</Label>
              <Input
                id="office_location"
                {...form.register('office_location')}
                placeholder="Ex: Bâtiment A, Étage 3, Bureau 301"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="bio">Biographie professionnelle</Label>
              <Textarea
                id="bio"
                {...form.register('bio')}
                placeholder="Décrivez votre parcours, vos domaines d'expertise, vos certifications..."
                rows={4}
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={completeDoctorProfileMutation.isPending}
            >
              {completeDoctorProfileMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Création du profil...
                </>
              ) : (
                <>
                  <UserCheck className="mr-2 h-4 w-4" />
                  Compléter mon profil
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default DoctorProfileCompletion;
