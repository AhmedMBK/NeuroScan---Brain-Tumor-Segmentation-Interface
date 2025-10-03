import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

// Schéma de validation conforme à la base de données treatments
const treatmentSchema = z.object({
  // Champs obligatoires
  patient_id: z.string().min(1, 'Le patient est requis'),
  prescribed_by_doctor_id: z.string().min(1, 'Le médecin prescripteur est requis'),
  treatment_type: z.string().min(1, 'Le type de traitement est requis'),
  start_date: z.string().min(1, 'La date de début est requise'),
  
  // Champs optionnels
  medication_name: z.string().optional(),
  dosage: z.string().optional(),
  frequency: z.string().optional(),
  duration: z.string().optional(),
  end_date: z.string().optional(),
  status: z.enum(['ACTIVE', 'COMPLETED', 'DISCONTINUED']).default('ACTIVE'),
  notes: z.string().optional(),
});

type TreatmentFormData = z.infer<typeof treatmentSchema>;

interface TreatmentFormProps {
  mode: 'create' | 'edit';
  initialData?: Partial<any>;
  onSubmit: (data: TreatmentFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
  patients?: Array<{ id: string; first_name: string; last_name: string }>;
  doctors?: Array<{ id: string; user: { first_name: string; last_name: string } }>;
}

const TreatmentForm: React.FC<TreatmentFormProps> = ({
  mode,
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  patients = [],
  doctors = [],
}) => {
  const form = useForm<TreatmentFormData>({
    resolver: zodResolver(treatmentSchema),
    defaultValues: {
      patient_id: initialData?.patient_id || '',
      prescribed_by_doctor_id: initialData?.prescribed_by_doctor_id || '',
      treatment_type: initialData?.treatment_type || '',
      medication_name: initialData?.medication_name || '',
      dosage: initialData?.dosage || '',
      frequency: initialData?.frequency || '',
      duration: initialData?.duration || '',
      start_date: initialData?.start_date || '',
      end_date: initialData?.end_date || '',
      status: initialData?.status || 'ACTIVE',
      notes: initialData?.notes || '',
    },
  });

  const handleSubmit = (data: TreatmentFormData) => {
    // Nettoyer les données avant envoi
    const cleanedData = {
      ...data,
      medication_name: data.medication_name || undefined,
      dosage: data.dosage || undefined,
      frequency: data.frequency || undefined,
      duration: data.duration || undefined,
      end_date: data.end_date || undefined,
      notes: data.notes || undefined,
    };

    onSubmit(cleanedData);
  };

  const treatmentTypes = [
    'Chimiothérapie',
    'Radiothérapie',
    'Immunothérapie',
    'Thérapie ciblée',
    'Chirurgie',
    'Hormonothérapie',
    'Soins palliatifs',
    'Autre'
  ];

  const frequencies = [
    '1 fois par jour',
    '2 fois par jour',
    '3 fois par jour',
    '1 fois par semaine',
    '2 fois par semaine',
    '1 fois par mois',
    'Selon besoin'
  ];

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>
          {mode === 'create' ? 'Nouveau Traitement' : 'Modifier Traitement'}
        </CardTitle>
        <CardDescription>
          {mode === 'create' 
            ? 'Prescrire un nouveau traitement pour un patient'
            : 'Modifier les informations du traitement'
          }
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            {/* Informations de base */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Informations de base</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="patient_id"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Patient *</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Sélectionner un patient" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {patients.map((patient) => (
                            <SelectItem key={patient.id} value={patient.id}>
                              {patient.first_name} {patient.last_name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="prescribed_by_doctor_id"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Médecin prescripteur *</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Sélectionner un médecin" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {doctors.map((doctor) => (
                            <SelectItem key={doctor.id} value={doctor.id}>
                              Dr. {doctor.user.first_name} {doctor.user.last_name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="treatment_type"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Type de traitement *</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Sélectionner le type" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {treatmentTypes.map((type) => (
                            <SelectItem key={type} value={type}>
                              {type}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="status"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Statut</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Sélectionner le statut" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="ACTIVE">Actif</SelectItem>
                          <SelectItem value="COMPLETED">Terminé</SelectItem>
                          <SelectItem value="DISCONTINUED">Arrêté</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            {/* Détails du médicament */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Détails du médicament</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="medication_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Nom du médicament</FormLabel>
                      <FormControl>
                        <Input placeholder="Temozolomide" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="dosage"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Dosage</FormLabel>
                      <FormControl>
                        <Input placeholder="150mg" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="frequency"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Fréquence</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Sélectionner la fréquence" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {frequencies.map((freq) => (
                            <SelectItem key={freq} value={freq}>
                              {freq}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="duration"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Durée</FormLabel>
                      <FormControl>
                        <Input placeholder="4 semaines" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            {/* Dates */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Période de traitement</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="start_date"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Date de début *</FormLabel>
                      <FormControl>
                        <Input type="date" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="end_date"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Date de fin</FormLabel>
                      <FormControl>
                        <Input type="date" {...field} />
                      </FormControl>
                      <FormDescription>
                        Optionnel - laissez vide pour un traitement en cours
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            {/* Notes */}
            <FormField
              control={form.control}
              name="notes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Notes</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Instructions spéciales, effets secondaires observés, etc."
                      className="resize-none h-24"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Actions */}
            <div className="flex justify-end space-x-4 pt-6">
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={isLoading}
              >
                Annuler
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? 'Enregistrement...' : mode === 'create' ? 'Créer' : 'Modifier'}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
};

export default TreatmentForm;
