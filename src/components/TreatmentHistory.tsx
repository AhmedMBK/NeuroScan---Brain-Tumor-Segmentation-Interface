import React from 'react';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';
import {
  Calendar,
  Clock,
  Pill,
  Stethoscope,
  FileText,
  Scissors,
  Radiation,
  CheckCircle,
  XCircle,
  AlertCircle,
  Activity
} from 'lucide-react';
import { useTreatments } from '@/hooks/api/useTreatments';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription
} from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';

interface TreatmentHistoryProps {
  patientId: string;
}

const TreatmentHistory: React.FC<TreatmentHistoryProps> = ({ patientId }) => {
  const { t } = useTranslation();

  // Récupérer les traitements depuis l'API
  const { data: treatments = [], isLoading, error } = useTreatments(patientId);

  // Filter completed treatments
  const completedTreatments = treatments.filter((treatment: any) =>
    treatment.status?.toUpperCase() === 'COMPLETED'
  );

  // Filter cancelled treatments
  const cancelledTreatments = treatments.filter((treatment: any) =>
    treatment.status?.toUpperCase() === 'CANCELLED'
  );

  // Sort treatments by date (newest first)
  const sortedCompletedTreatments = [...completedTreatments].sort((a: any, b: any) =>
    new Date(b.start_date).getTime() - new Date(a.start_date).getTime()
  );

  const sortedCancelledTreatments = [...cancelledTreatments].sort((a: any, b: any) =>
    new Date(b.start_date).getTime() - new Date(a.start_date).getTime()
  );

  // Get icon based on treatment type
  const getTreatmentIcon = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'chimiothérapie':
      case 'chemotherapy':
        return <Activity className="h-5 w-5 text-purple-500" />;
      case 'chirurgie':
      case 'surgery':
        return <Scissors className="h-5 w-5 text-red-500" />;
      case 'radiothérapie':
      case 'radiation':
        return <Radiation className="h-5 w-5 text-amber-500" />;
      default:
        return <Pill className="h-5 w-5 text-blue-500" />;
    }
  };

  // Get status icon
  const getStatusIcon = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'COMPLETED':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'CANCELLED':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-amber-500" />;
    }
  };

  // Gestion du loading
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t('treatments.treatmentHistory')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-medical mx-auto mb-4"></div>
              <p className="text-muted-foreground">Chargement des traitements...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Gestion des erreurs
  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t('treatments.treatmentHistory')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <AlertCircle className="h-8 w-8 text-destructive mx-auto mb-4" />
              <p className="text-destructive">Erreur lors du chargement des traitements</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (completedTreatments.length === 0 && cancelledTreatments.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t('treatments.treatmentHistory')}</CardTitle>
          <CardDescription>{t('treatments.treatmentHistoryDescription')}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center py-10">
          <FileText className="h-10 w-10 text-muted-foreground mb-4" />
          <p className="text-muted-foreground">{t('treatments.noTreatmentHistory')}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('treatments.treatmentHistory')}</CardTitle>
        <CardDescription>{t('treatments.treatmentHistoryDescription')}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Completed treatments */}
        {sortedCompletedTreatments.length > 0 && (
          <div>
            <h4 className="font-medium flex items-center gap-2 mb-3">
              <CheckCircle className="h-4 w-4 text-green-500" />
              {t('treatments.completedTreatments')}
            </h4>
            <Accordion type="single" collapsible className="w-full">
              {sortedCompletedTreatments.map((treatment, index) => (
                <AccordionItem key={treatment.id} value={treatment.id}>
                  <AccordionTrigger className="hover:no-underline">
                    <div className="flex items-center gap-3 text-left">
                      <div>
                        {getTreatmentIcon(treatment.treatment_type)}
                      </div>
                      <div>
                        <div className="font-medium">{treatment.treatment_name || treatment.medication_name}</div>
                        <div className="text-xs text-muted-foreground">
                          {treatment.treatment_type} • {format(new Date(treatment.start_date), 'PP')}
                          {treatment.end_date && ` - ${format(new Date(treatment.end_date), 'PP')}`}
                        </div>
                      </div>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent>
                    <div className="pt-2 pb-1 px-1">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <div className="flex items-center gap-2 text-sm">
                            <Calendar className="h-4 w-4 text-muted-foreground" />
                            <span className="text-muted-foreground">{t('treatments.startDate')}:</span>
                            <span>{format(new Date(treatment.start_date), 'PPP')}</span>
                          </div>

                          {treatment.end_date && (
                            <div className="flex items-center gap-2 text-sm">
                              <Calendar className="h-4 w-4 text-muted-foreground" />
                              <span className="text-muted-foreground">{t('treatments.endDate')}:</span>
                              <span>{format(new Date(treatment.end_date), 'PPP')}</span>
                            </div>
                          )}

                          {treatment.frequency && (
                            <div className="flex items-center gap-2 text-sm">
                              <Clock className="h-4 w-4 text-muted-foreground" />
                              <span className="text-muted-foreground">{t('treatments.frequency')}:</span>
                              <span>{treatment.frequency}</span>
                            </div>
                          )}

                          {treatment.dosage && (
                            <div className="flex items-center gap-2 text-sm">
                              <Pill className="h-4 w-4 text-muted-foreground" />
                              <span className="text-muted-foreground">{t('treatments.dosage')}:</span>
                              <span>{treatment.dosage}</span>
                            </div>
                          )}
                        </div>

                        <div className="space-y-2">
                          <div className="flex items-center gap-2 text-sm">
                            <Stethoscope className="h-4 w-4 text-muted-foreground" />
                            <span className="text-muted-foreground">{t('treatments.prescribedBy')}:</span>
                            <span>Dr. {treatment.doctor_name || 'Non spécifié'}</span>
                          </div>


                        </div>
                      </div>

                      <div className="pt-3 mt-2 border-t">
                        <div className="text-sm text-muted-foreground mb-1">{t('treatments.notes')}:</div>
                        <p className="text-sm">{treatment.notes}</p>
                      </div>
                    </div>
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </div>
        )}

        {/* Cancelled treatments */}
        {sortedCancelledTreatments.length > 0 && (
          <div>
            <h4 className="font-medium flex items-center gap-2 mb-3">
              <XCircle className="h-4 w-4 text-red-500" />
              {t('treatments.cancelledTreatments')}
            </h4>
            <Accordion type="single" collapsible className="w-full">
              {sortedCancelledTreatments.map((treatment, index) => (
                <AccordionItem key={treatment.id} value={treatment.id}>
                  <AccordionTrigger className="hover:no-underline">
                    <div className="flex items-center gap-3 text-left">
                      <div>
                        {getTreatmentIcon(treatment.treatment_type)}
                      </div>
                      <div>
                        <div className="font-medium">{treatment.treatment_name || treatment.medication_name}</div>
                        <div className="text-xs text-muted-foreground">
                          {treatment.treatment_type} • {format(new Date(treatment.start_date), 'PP')}
                          {treatment.end_date && ` - ${format(new Date(treatment.end_date), 'PP')}`}
                        </div>
                      </div>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent>
                    <div className="pt-2 pb-1 px-1">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <div className="flex items-center gap-2 text-sm">
                            <Calendar className="h-4 w-4 text-muted-foreground" />
                            <span className="text-muted-foreground">{t('treatments.startDate')}:</span>
                            <span>{format(new Date(treatment.start_date || treatment.startDate), 'PPP')}</span>
                          </div>

                          {(treatment.end_date || treatment.endDate) && (
                            <div className="flex items-center gap-2 text-sm">
                              <Calendar className="h-4 w-4 text-muted-foreground" />
                              <span className="text-muted-foreground">{t('treatments.endDate')}:</span>
                              <span>{format(new Date(treatment.end_date || treatment.endDate), 'PPP')}</span>
                            </div>
                          )}

                          {treatment.frequency && (
                            <div className="flex items-center gap-2 text-sm">
                              <Clock className="h-4 w-4 text-muted-foreground" />
                              <span className="text-muted-foreground">{t('treatments.frequency')}:</span>
                              <span>{treatment.frequency}</span>
                            </div>
                          )}
                        </div>

                        <div className="space-y-2">
                          <div className="flex items-center gap-2 text-sm">
                            <Stethoscope className="h-4 w-4 text-muted-foreground" />
                            <span className="text-muted-foreground">{t('treatments.prescribedBy')}:</span>
                            <span>{treatment.doctor}</span>
                          </div>


                        </div>
                      </div>

                      <div className="pt-3 mt-2 border-t">
                        <div className="text-sm text-muted-foreground mb-1">{t('treatments.notes')}:</div>
                        <p className="text-sm">{treatment.notes}</p>
                      </div>
                    </div>
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </div>
        )}
      </CardContent>

    </Card>
  );
};

export default TreatmentHistory;
