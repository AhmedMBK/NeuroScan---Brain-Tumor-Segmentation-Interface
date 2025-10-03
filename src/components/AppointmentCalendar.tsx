import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { format, isSameDay, isToday, isFuture, isPast, addMonths } from 'date-fns';
import {
  Calendar as CalendarIcon,
  Clock,
  User,
  FileText,
  Plus,
  CheckCircle,
  XCircle,
  AlertCircle,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { useAppointments, useUpdateAppointment } from '@/hooks/api/useAppointments';
import RoleBasedAccess from '@/components/common/RoleBasedAccess';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
  CardFooter
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calendar } from '@/components/ui/calendar';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,
} from '@/components/ui/dialog';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface AppointmentCalendarProps {
  patientId?: string; // Optionnel pour filtrer par patient
}

const AppointmentCalendar: React.FC<AppointmentCalendarProps> = ({ patientId }) => {
  const { t } = useTranslation();
  const [date, setDate] = useState<Date>(new Date());
  const [selectedAppointment, setSelectedAppointment] = useState<any | null>(null);

  // Récupérer les rendez-vous depuis l'API
  const { data: appointments = [], isLoading, error } = useAppointments(patientId);
  const updateAppointmentMutation = useUpdateAppointment();

  // Filtrer par patient si spécifié
  const filteredAppointments = patientId
    ? appointments.filter((apt: any) => apt.patient_id === patientId)
    : appointments;

  // Filter upcoming appointments
  const upcomingAppointments = filteredAppointments.filter((appointment: any) =>
    isFuture(new Date(appointment.appointment_date)) && appointment.status === 'SCHEDULED'
  ).sort((a: any, b: any) => new Date(a.appointment_date).getTime() - new Date(b.appointment_date).getTime());

  // Get appointments for the selected date
  const appointmentsForDate = filteredAppointments.filter((appointment: any) =>
    isSameDay(new Date(appointment.appointment_date), date)
  ).sort((a: any, b: any) => {
    // Sort by time
    const timeA = a.appointment_time || '09:00';
    const timeB = b.appointment_time || '09:00';
    return timeA.localeCompare(timeB);
  });

  // Gestion des actions sur les rendez-vous
  const handleUpdateAppointment = async (appointmentId: string, status: string) => {
    try {
      await updateAppointmentMutation.mutateAsync({
        id: appointmentId,
        appointmentData: { status }
      });
    } catch (error) {
      console.error('Erreur lors de la mise à jour:', error);
    }
  };

  // Get status badge variant
  const getStatusBadgeVariant = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'COMPLETED':
        return 'default';
      case 'SCHEDULED':
        return 'outline';
      case 'CANCELLED':
        return 'destructive';
      case 'NO_SHOW':
        return 'secondary';
      default:
        return 'outline';
    }
  };

  // Get status icon
  const getStatusIcon = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'COMPLETED':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'SCHEDULED':
        return <CalendarIcon className="h-4 w-4 text-blue-500" />;
      case 'CANCELLED':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'NO_SHOW':
        return <AlertCircle className="h-4 w-4 text-amber-500" />;
      default:
        return <CalendarIcon className="h-4 w-4" />;
    }
  };

  // Function to highlight dates with appointments
  const isDayWithAppointment = (day: Date) => {
    return filteredAppointments.some((appointment: any) =>
      isSameDay(new Date(appointment.appointment_date), day)
    );
  };

  // Gestion du loading et des erreurs
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t('appointments.appointmentCalendar')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-medical mx-auto mb-4"></div>
              <p className="text-muted-foreground">Chargement des rendez-vous...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t('appointments.appointmentCalendar')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <AlertCircle className="h-8 w-8 text-destructive mx-auto mb-4" />
              <p className="text-destructive">Erreur lors du chargement des rendez-vous</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('appointments.appointmentCalendar')}</CardTitle>
        <CardDescription>{t('appointments.appointmentCalendarDescription')}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Calendar */}
          <div>
            <Calendar
              mode="single"
              selected={date}
              onSelect={(newDate) => newDate && setDate(newDate)}
              className="rounded-md border"
              modifiers={{
                appointment: (date) => isDayWithAppointment(date),
                today: (date) => isToday(date)
              }}
              modifiersClassNames={{
                appointment: 'bg-medical/10 font-medium text-medical',
                today: 'bg-medical/20 font-bold text-medical'
              }}
            />
          </div>

          {/* Appointments for selected date */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium">
                {format(date, 'PPP')}
              </h3>
              <RoleBasedAccess requiredPermissions={['can_manage_appointments']}>
                <Button variant="outline" size="sm">
                  <Plus className="mr-2 h-4 w-4" />
                  {t('appointments.addAppointment')}
                </Button>
              </RoleBasedAccess>
            </div>

            {appointmentsForDate.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <CalendarIcon className="h-10 w-10 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">{t('appointments.noAppointmentsForDate')}</p>
              </div>
            ) : (
              <div className="space-y-3">
                {appointmentsForDate.map(appointment => (
                  <Dialog key={appointment.id}>
                    <DialogTrigger asChild>
                      <div
                        className="flex items-start justify-between p-3 rounded-md border cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800"
                        onClick={() => setSelectedAppointment(appointment)}
                      >
                        <div className="flex items-start gap-3">
                          <div className="mt-0.5">
                            {getStatusIcon(appointment.status)}
                          </div>
                          <div>
                            <div className="font-medium">{appointment.purpose || 'Consultation'}</div>
                            <div className="text-xs text-muted-foreground">
                              {appointment.appointment_time} • Dr. {appointment.doctor_name || 'Non assigné'}
                            </div>
                          </div>
                        </div>
                        <Badge variant={getStatusBadgeVariant(appointment.status)}>
                          {appointment.status}
                        </Badge>
                      </div>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>{appointment.purpose || 'Consultation'}</DialogTitle>
                        <DialogDescription>
                          {format(new Date(appointment.appointment_date), 'PPP')} • {appointment.appointment_time}
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4 py-2">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <div className="flex items-center gap-2 text-sm">
                              <CalendarIcon className="h-4 w-4 text-muted-foreground" />
                              <span className="text-muted-foreground">{t('appointments.date')}:</span>
                              <span>{format(new Date(appointment.appointment_date), 'PPP')}</span>
                            </div>

                            <div className="flex items-center gap-2 text-sm">
                              <Clock className="h-4 w-4 text-muted-foreground" />
                              <span className="text-muted-foreground">{t('appointments.time')}:</span>
                              <span>{appointment.appointment_time}</span>
                            </div>

                            <div className="flex items-center gap-2 text-sm">
                              <User className="h-4 w-4 text-muted-foreground" />
                              <span className="text-muted-foreground">{t('appointments.doctor')}:</span>
                              <span>Dr. {appointment.doctor_name || 'Non assigné'}</span>
                            </div>
                          </div>

                          <div className="space-y-2">
                            <div className="flex items-center gap-2 text-sm">
                              <FileText className="h-4 w-4 text-muted-foreground" />
                              <span className="text-muted-foreground">{t('appointments.purpose')}:</span>
                              <span>{appointment.purpose || 'Consultation'}</span>
                            </div>

                            <div className="flex items-center gap-2 text-sm">
                              {getStatusIcon(appointment.status)}
                              <span className="text-muted-foreground">{t('appointments.status')}:</span>
                              <Badge variant={getStatusBadgeVariant(appointment.status)}>
                                {appointment.status}
                              </Badge>
                            </div>

                            <div className="flex items-center gap-2 text-sm">
                              <CalendarIcon className="h-4 w-4 text-muted-foreground" />
                              <span className="text-muted-foreground">Type:</span>
                              <span>{appointment.appointment_type || 'Consultation'}</span>
                            </div>
                          </div>
                        </div>

                        <div className="pt-2 border-t">
                          <div className="text-sm text-muted-foreground mb-1">{t('appointments.notes')}:</div>
                          <p className="text-sm">{appointment.notes || 'Aucune note'}</p>
                        </div>
                      </div>
                      <RoleBasedAccess requiredPermissions={['can_manage_appointments']}>
                        <div className="flex justify-between">
                          {appointment.status?.toUpperCase() === 'SCHEDULED' && (
                            <>
                              <Button
                                variant="outline"
                                className="text-red-500"
                                onClick={() => handleUpdateAppointment(appointment.id, 'CANCELLED')}
                                disabled={updateAppointmentMutation.isPending}
                              >
                                <XCircle className="mr-2 h-4 w-4" />
                                {t('appointments.cancel')}
                              </Button>
                              <Button
                                onClick={() => handleUpdateAppointment(appointment.id, 'COMPLETED')}
                                disabled={updateAppointmentMutation.isPending}
                              >
                                <CheckCircle className="mr-2 h-4 w-4" />
                                {t('appointments.confirm')}
                              </Button>
                            </>
                          )}
                          {appointment.status?.toUpperCase() === 'COMPLETED' && (
                            <Button className="ml-auto">
                              <FileText className="mr-2 h-4 w-4" />
                              {t('appointments.viewSummary')}
                            </Button>
                          )}
                        </div>
                      </RoleBasedAccess>
                    </DialogContent>
                  </Dialog>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Upcoming appointments */}
        <div className="pt-4 border-t">
          <h3 className="font-medium mb-3">{t('appointments.upcomingAppointments')}</h3>

          {upcomingAppointments.length === 0 ? (
            <div className="text-center py-4">
              <p className="text-muted-foreground">{t('appointments.noUpcomingAppointments')}</p>
            </div>
          ) : (
            <div className="space-y-3">
              {upcomingAppointments.slice(0, 3).map(appointment => (
                <div key={appointment.id} className="flex items-start justify-between p-3 rounded-md bg-slate-50 dark:bg-slate-800">
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5">
                      <CalendarIcon className="h-4 w-4 text-blue-500" />
                    </div>
                    <div>
                      <div className="font-medium">{appointment.purpose || 'Consultation'}</div>
                      <div className="text-xs text-muted-foreground">
                        {format(new Date(appointment.appointment_date), 'PPP')} • {appointment.appointment_time} • Dr. {appointment.doctor_name || 'Non assigné'}
                      </div>
                    </div>
                  </div>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <FileText className="h-4 w-4" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{t('appointments.viewDetails')}</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
              ))}

              {upcomingAppointments.length > 3 && (
                <Button variant="outline" className="w-full">
                  {t('appointments.viewAllAppointments')} ({upcomingAppointments.length})
                </Button>
              )}
            </div>
          )}
        </div>
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button variant="outline">
          <ChevronLeft className="mr-2 h-4 w-4" />
          {format(addMonths(date, -1), 'MMMM yyyy')}
        </Button>
        <Button variant="outline">
          {format(addMonths(date, 1), 'MMMM yyyy')}
          <ChevronRight className="ml-2 h-4 w-4" />
        </Button>
      </CardFooter>
    </Card>
  );
};

export default AppointmentCalendar;
