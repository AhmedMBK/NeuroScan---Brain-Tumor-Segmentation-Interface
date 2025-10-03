import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
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
import { Patient } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';

// Schéma de validation conforme à la base de données
const patientSchema = z.object({
  // Champs obligatoires
  first_name: z.string().min(2, 'Le prénom doit contenir au moins 2 caractères'),
  last_name: z.string().min(2, 'Le nom doit contenir au moins 2 caractères'),
  date_of_birth: z.string().min(1, 'La date de naissance est requise'),
  gender: z.enum(['MALE', 'FEMALE'], {
    required_error: 'Le genre est requis',
  }),

  // Champs optionnels
  email: z.string().email('Email invalide').optional().or(z.literal('')),
  phone: z.string().optional(),
  address: z.string().optional(),
  blood_type: z.enum(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']).optional(),
  height: z.number().int().positive().optional().or(z.literal('')), // Integer en cm
  weight: z.number().positive().optional().or(z.literal('')), // Decimal en kg

  // Champs JSON et texte
  emergency_contact_name: z.string().optional(),
  emergency_contact_phone: z.string().optional(),
  emergency_contact_relationship: z.string().optional(),
  medical_history_allergies: z.string().optional(),
  medical_history_conditions: z.string().optional(),
  notes: z.string().optional(),

  // Médecin assigné
  assigned_doctor_id: z.string().optional(),
});

type PatientFormData = z.infer<typeof patientSchema>;

interface PatientFormProps {
  mode: 'create' | 'edit';
  initialData?: Partial<Patient>;
  onSubmit: (data: PatientFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

const PatientForm: React.FC<PatientFormProps> = ({
  mode,
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
}) => {
  // Récupérer l'utilisateur connecté
  const { currentUser } = useAuth();

  // Les admins n'ont pas besoin de ce formulaire - ils créent des patients via le formulaire utilisateur
  // Les doctors et secretaries ont l'assignation automatique
  const showAssignedDoctorField = false;

  const form = useForm<PatientFormData>({
    resolver: zodResolver(patientSchema),
    defaultValues: {
      // Champs obligatoires
      first_name: initialData?.first_name || '',
      last_name: initialData?.last_name || '',
      date_of_birth: initialData?.date_of_birth || '',
      gender: initialData?.gender || undefined,

      // Champs optionnels
      email: initialData?.email || '',
      phone: initialData?.phone || '',
      address: initialData?.address || '',
      blood_type: initialData?.blood_type || undefined,
      height: initialData?.height || '',
      weight: initialData?.weight || '',

      // Contact d'urgence (décomposé du JSON)
      emergency_contact_name: initialData?.emergency_contact?.name || '',
      emergency_contact_phone: initialData?.emergency_contact?.phone || '',
      emergency_contact_relationship: initialData?.emergency_contact?.relationship || '',

      // Historique médical (décomposé du JSON)
      medical_history_allergies: initialData?.medical_history?.allergies || '',
      medical_history_conditions: initialData?.medical_history?.history || '',

      notes: initialData?.notes || '',
      assigned_doctor_id: initialData?.assigned_doctor_id || '',
    },
  });

  const handleSubmit = (data: PatientFormData) => {
    // Adapter les données au format attendu par l'API backend
    const cleanedData = {
      // Champs de base
      first_name: data.first_name,
      last_name: data.last_name,
      date_of_birth: data.date_of_birth,
      gender: data.gender,

      // Champs optionnels
      email: data.email || undefined,
      phone: data.phone || undefined,
      address: data.address || undefined,
      blood_type: data.blood_type || undefined,
      height: data.height ? Number(data.height) : undefined,
      weight: data.weight ? Number(data.weight) : undefined,

      // Contact d'urgence - champs séparés comme attendu par l'API
      emergency_contact_name: data.emergency_contact_name || undefined,
      emergency_contact_phone: data.emergency_contact_phone || undefined,
      emergency_contact_relationship: data.emergency_contact_relationship || undefined,

      // Historique médical - champs séparés comme attendu par l'API
      medical_history: data.medical_history_conditions || undefined,
      allergies: data.medical_history_allergies || undefined,

      notes: data.notes || undefined,
      assigned_doctor_id: (data.assigned_doctor_id && data.assigned_doctor_id !== 'none') ? data.assigned_doctor_id : undefined,
    };

    onSubmit(cleanedData);
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>
          {mode === 'create' ? 'Nouveau Patient' : 'Modifier Patient'}
        </CardTitle>
        <CardDescription>
          {mode === 'create'
            ? 'Créer un nouveau dossier patient dans le système'
            : 'Modifier les informations du patient'
          }
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            {/* Informations personnelles */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="first_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Prénom *</FormLabel>
                    <FormControl>
                      <Input placeholder="Jean" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="last_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Nom *</FormLabel>
                    <FormControl>
                      <Input placeholder="Dupont" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="date_of_birth"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Date de naissance *</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="gender"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Genre *</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Sélectionner le genre" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="MALE">Masculin</SelectItem>
                        <SelectItem value="FEMALE">Féminin</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {/* Contact */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input type="email" placeholder="jean.dupont@email.com" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="phone"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Téléphone</FormLabel>
                    <FormControl>
                      <Input placeholder="01 23 45 67 89" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="address"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Adresse</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="123 Rue de la Paix, 75001 Paris"
                      className="resize-none"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Informations médicales */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Informations médicales</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <FormField
                  control={form.control}
                  name="blood_type"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Groupe sanguin</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Sélectionner" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="A+">A+</SelectItem>
                          <SelectItem value="A-">A-</SelectItem>
                          <SelectItem value="B+">B+</SelectItem>
                          <SelectItem value="B-">B-</SelectItem>
                          <SelectItem value="O+">O+</SelectItem>
                          <SelectItem value="O-">O-</SelectItem>
                          <SelectItem value="AB+">AB+</SelectItem>
                          <SelectItem value="AB-">AB-</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="height"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Taille (cm)</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          placeholder="175"
                          {...field}
                          onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) : '')}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="weight"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Poids (kg)</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          step="0.1"
                          placeholder="70.5"
                          {...field}
                          onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) : '')}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            {/* Contact d'urgence */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Contact d'urgence</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <FormField
                  control={form.control}
                  name="emergency_contact_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Nom du contact</FormLabel>
                      <FormControl>
                        <Input placeholder="Marie Dupont" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="emergency_contact_phone"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Téléphone</FormLabel>
                      <FormControl>
                        <Input placeholder="06 12 34 56 78" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="emergency_contact_relationship"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Relation</FormLabel>
                      <FormControl>
                        <Input placeholder="Épouse, Enfant, Parent..." {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            {/* Historique médical */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Historique médical</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="medical_history_allergies"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Allergies</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Pénicilline, Aspirine, Iode... (séparées par des virgules)"
                          className="resize-none"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="medical_history_conditions"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Conditions chroniques</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Hypertension, Diabète... (séparées par des virgules)"
                          className="resize-none"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            {/* Médecin assigné (visible uniquement pour les admins) */}
            {showAssignedDoctorField && (
              <FormField
                control={form.control}
                name="assigned_doctor_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Médecin assigné</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Sélectionner un médecin (optionnel)" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="none">Aucun médecin assigné</SelectItem>
                        {doctors.map((doctor: any) => (
                          <SelectItem key={doctor.id} value={doctor.id}>
                            Dr. {doctor.user?.first_name} {doctor.user?.last_name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      Seuls les admins peuvent assigner manuellement un médecin.
                      Les médecins et secrétaires créent automatiquement des patients qui leur sont assignés.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}

            {/* Notes */}
            <FormField
              control={form.control}
              name="notes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Notes</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Notes additionnelles sur le patient..."
                      className="resize-none h-24"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Information sur l'assignation automatique */}
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
                📋 Assignation automatique
              </h4>
              <p className="text-sm text-blue-700 dark:text-blue-300">
                {currentUser?.role === 'DOCTOR' &&
                  "Ce patient sera automatiquement assigné à votre profil médecin."
                }
                {currentUser?.role === 'SECRETARY' &&
                  "Ce patient sera automatiquement assigné au médecin auquel vous êtes rattaché(e)."
                }
                {currentUser?.role === 'ADMIN' &&
                  "En tant qu'administrateur, utilisez le formulaire de création d'utilisateur pour créer des patients avec assignation spécifique."
                }
              </p>
            </div>

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

export default PatientForm;
