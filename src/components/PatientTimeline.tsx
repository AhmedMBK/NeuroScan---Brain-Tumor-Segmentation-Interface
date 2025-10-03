import React from 'react';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';
import {
  Calendar,
  FileText,
  Pill,
  Activity,
  Upload,
  Brain,
  User,
  Clock
} from 'lucide-react';
import { useTreatments } from '@/hooks/api/useTreatments';
import { useAppointments } from '@/hooks/api/useAppointments';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface TimelineEvent {
  id: string;
  type: 'creation' | 'appointment' | 'treatment' | 'image' | 'segmentation';
  date: string;
  title: string;
  description: string;
  status?: string;
  icon: React.ReactNode;
}

interface PatientTimelineProps {
  patientId: string;
  patientCreatedAt: string;
}

const PatientTimeline: React.FC<PatientTimelineProps> = ({ patientId, patientCreatedAt }) => {
  const { t } = useTranslation();

  // Récupérer les données depuis les APIs
  const { data: treatments = [], isLoading: treatmentsLoading } = useTreatments(patientId);
  const { data: appointments = [], isLoading: appointmentsLoading } = useAppointments();

  // Filtrer les rendez-vous du patient
  const patientAppointments = appointments.filter((apt: any) => apt.patient_id === patientId);

  // Créer les événements de la timeline
  const createTimelineEvents = (): TimelineEvent[] => {
    const events: TimelineEvent[] = [];

    // Événement de création du patient
    events.push({
      id: 'creation',
      type: 'creation',
      date: patientCreatedAt,
      title: 'Création du dossier patient',
      description: 'Le dossier patient a été créé dans le système CereBloom',
      icon: <User className="h-4 w-4 text-blue-500" />
    });

    // Événements de rendez-vous
    patientAppointments.forEach((appointment: any) => {
      events.push({
        id: appointment.id,
        type: 'appointment',
        date: appointment.appointment_date,
        title: `Rendez-vous - ${appointment.appointment_type || 'Consultation'}`,
        description: `${appointment.notes || 'Consultation médicale'}`,
        status: appointment.status,
        icon: <Calendar className="h-4 w-4 text-green-500" />
      });
    });

    // Événements de traitements
    treatments.forEach((treatment: any) => {
      events.push({
        id: treatment.id,
        type: 'treatment',
        date: treatment.start_date,
        title: `Traitement - ${treatment.treatment_type}`,
        description: treatment.medication_name ?
          `Médicament: ${treatment.medication_name} - ${treatment.dosage || ''}` :
          treatment.notes || 'Traitement prescrit',
        status: treatment.status,
        icon: <Pill className="h-4 w-4 text-purple-500" />
      });
    });

    // Trier par date (plus récent en premier)
    return events.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  };

  const timelineEvents = createTimelineEvents();

  const getStatusBadgeVariant = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'COMPLETED':
      case 'ACTIVE':
        return 'default';
      case 'SCHEDULED':
        return 'outline';
      case 'CANCELLED':
        return 'destructive';
      default:
        return 'secondary';
    }
  };

  if (treatmentsLoading || appointmentsLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Historique du Patient</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-medical"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Historique du Patient</CardTitle>
        <CardDescription>
          Chronologie des consultations, examens et traitements
        </CardDescription>
      </CardHeader>
      <CardContent>
        {timelineEvents.length === 0 ? (
          <div className="text-center py-8">
            <Activity className="h-10 w-10 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">Aucun événement dans l'historique</p>
          </div>
        ) : (
          <div className="space-y-4">
            {timelineEvents.map((event, index) => (
              <div key={event.id} className="relative">
                {/* Ligne de connexion */}
                {index < timelineEvents.length - 1 && (
                  <div className="absolute left-6 top-12 w-0.5 h-8 bg-border"></div>
                )}

                <div className="flex items-start gap-4">
                  {/* Icône */}
                  <div className="flex-shrink-0 w-12 h-12 rounded-full bg-background border-2 border-border flex items-center justify-center">
                    {event.icon}
                  </div>

                  {/* Contenu */}
                  <div className="flex-grow min-w-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-grow">
                        <h4 className="font-medium text-sm">{event.title}</h4>
                        <p className="text-sm text-muted-foreground mt-1">
                          {event.description}
                        </p>
                        <div className="flex items-center gap-2 mt-2">
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Clock className="h-3 w-3" />
                            {format(new Date(event.date), 'PPP')}
                          </div>
                          {event.status && (
                            <Badge variant={getStatusBadgeVariant(event.status)} className="text-xs">
                              {event.status}
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PatientTimeline;
