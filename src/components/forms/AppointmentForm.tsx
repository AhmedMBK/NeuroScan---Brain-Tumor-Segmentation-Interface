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

// Schéma de validation conforme à la base de données appointments
const appointmentSchema = z.object({
  // Champs obligatoires
  patient_id: z.string().min(1, 'Le patient est requis'),
  doctor_id: z.string().min(1, 'Le médecin est requis'),
  appointment_date: z.string().min(1, 'La date est requise'),
  appointment_time: z.string().min(1, 'L\'heure est requise'),
  
  // Champs optionnels
  appointment_type: z.string().optional(),
  status: z.enum(['SCHEDULED', 'COMPLETED', 'CANCELLED', 'NO_SHOW']).default('SCHEDULED'),
  notes: z.string().optional(),
  previous_appointment_id: z.string().optional(),
});

type AppointmentFormData = z.infer<typeof appointmentSchema>;

interface AppointmentFormProps {
  mode: 'create' | 'edit';
  initialData?: Partial<any>;
  onSubmit: (data: AppointmentFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
  patients?: Array<{ id: string; first_name: string; last_name: string }>;
  doctors?: Array<{ id: string; user: { first_name: string; last_name: string } }>;
}

const AppointmentForm: React.FC<AppointmentFormProps> = ({
  mode,
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  patients = [],
  doctors = [],
}) => {
  const form = useForm<AppointmentFormData>({
    resolver: zodResolver(appointmentSchema),
    defaultValues: {
      patient_id: initialData?.patient_id || '',
      doctor_id: initialData?.doctor_id || '',
      appointment_date: initialData?.appointment_date || '',
      appointment_time: initialData?.appointment_time || '',
      appointment_type: initialData?.appointment_type || '',
      status: initialData?.status || 'SCHEDULED',
      notes: initialData?.notes || '',
      previous_appointment_id: initialData?.previous_appointment_id || '',
    },
  });

  const handleSubmit = (data: AppointmentFormData) => {
    // Nettoyer les données avant envoi
    const cleanedData = {
      ...data,
      appointment_type: data.appointment_type || undefined,
      notes: data.notes || undefined,
      previous_appointment_id: data.previous_appointment_id || undefined,
    };

    onSubmit(cleanedData);
  };

  const appointmentTypes = [
    'Consultation',
    'Suivi',
    'Contrôle',
    'Urgence',
    'Première consultation',
    'Consultation de résultats',
    'Consultation pré-opératoire',
    'Consultation post-opératoire'
  ];

  const timeSlots = [
    '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
    '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30',
    '16:00', '16:30', '17:00', '17:30', '18:00'
  ];

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>
          {mode === 'create' ? 'Nouveau Rendez-vous' : 'Modifier Rendez-vous'}
        </CardTitle>
        <CardDescription>
          {mode === 'create' 
            ? 'Planifier un nouveau rendez-vous médical'
            : 'Modifier les informations du rendez-vous'
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
                  name="doctor_id"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Médecin *</FormLabel>
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
                  name="appointment_type"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Type de rendez-vous</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Sélectionner le type" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {appointmentTypes.map((type) => (
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
                          <SelectItem value="SCHEDULED">Planifié</SelectItem>
                          <SelectItem value="COMPLETED">Terminé</SelectItem>
                          <SelectItem value="CANCELLED">Annulé</SelectItem>
                          <SelectItem value="NO_SHOW">Absent</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            {/* Date et heure */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Date et heure</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="appointment_date"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Date *</FormLabel>
                      <FormControl>
                        <Input type="date" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="appointment_time"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Heure *</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Sélectionner l'heure" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {timeSlots.map((time) => (
                            <SelectItem key={time} value={time}>
                              {time}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
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
                      placeholder="Motif de consultation, instructions spéciales..."
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

export default AppointmentForm;
