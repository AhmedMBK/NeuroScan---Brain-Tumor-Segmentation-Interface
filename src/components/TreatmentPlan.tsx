import React from 'react';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';
import {
  Calendar,
  Clock,
  Pill,
  Stethoscope,
  Scissors,
  Radiation,
  Activity
} from 'lucide-react';
import { useTreatments } from '@/hooks/api/useTreatments';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
  CardFooter
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

interface TreatmentPlanProps {
  patientId?: string;
}

const TreatmentPlan: React.FC<TreatmentPlanProps> = ({ patientId }) => {
  const { t } = useTranslation();

  // Récupérer les traitements depuis l'API
  const { data: treatments = [], isLoading, error } = useTreatments(patientId);

  // Filter active treatments
  const activeTreatments = treatments.filter((treatment: any) =>
    treatment.status?.toUpperCase() === 'ACTIVE' || treatment.status?.toUpperCase() === 'SCHEDULED'
  );

  // Get the most recent active treatment
  const primaryTreatment = activeTreatments.length > 0
    ? activeTreatments.sort((a: any, b: any) =>
        new Date(b.start_date || b.startDate).getTime() - new Date(a.start_date || a.startDate).getTime()
      )[0]
    : null;

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t('treatments.currentTreatmentPlan')}</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-10">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-medical"></div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t('treatments.currentTreatmentPlan')}</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center py-10">
          <AlertCircle className="h-10 w-10 text-destructive mb-4" />
          <p className="text-muted-foreground">{t('common.errorLoadingData')}</p>
        </CardContent>
      </Card>
    );
  }

  if (activeTreatments.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t('treatments.currentTreatmentPlan')}</CardTitle>
          <CardDescription>{t('treatments.currentTreatmentPlanDescription')}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center py-10">
          <AlertCircle className="h-10 w-10 text-muted-foreground mb-4" />
          <p className="text-muted-foreground">{t('treatments.noActiveTreatments')}</p>
        </CardContent>
        <CardFooter>
          <Button variant="outline" className="w-full">
            <Pill className="mr-2 h-4 w-4" />
            {t('treatments.createTreatmentPlan')}
          </Button>
        </CardFooter>
      </Card>
    );
  }



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

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('treatments.currentTreatmentPlan')}</CardTitle>
        <CardDescription>{t('treatments.currentTreatmentPlanDescription')}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Primary treatment */}
        {primaryTreatment && (
          <div className="space-y-4">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <div className="mt-1">
                  {getTreatmentIcon(primaryTreatment.treatment_type || primaryTreatment.type)}
                </div>
                <div>
                  <h3 className="font-medium">{primaryTreatment.treatment_name || primaryTreatment.name}</h3>
                  <p className="text-sm text-muted-foreground">{primaryTreatment.treatment_type || primaryTreatment.type}</p>
                </div>
              </div>
              <Badge variant={primaryTreatment.status?.toUpperCase() === 'ACTIVE' ? 'default' : 'outline'}>
                {primaryTreatment.status}
              </Badge>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">{t('treatments.startDate')}:</span>
                  <span>{format(new Date(primaryTreatment.start_date || primaryTreatment.startDate), 'PPP')}</span>
                </div>

                {(primaryTreatment.end_date || primaryTreatment.endDate) && (
                  <div className="flex items-center gap-2 text-sm">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">{t('treatments.endDate')}:</span>
                    <span>{format(new Date(primaryTreatment.end_date || primaryTreatment.endDate), 'PPP')}</span>
                  </div>
                )}

                {primaryTreatment.frequency && (
                  <div className="flex items-center gap-2 text-sm">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">{t('treatments.frequency')}:</span>
                    <span>{primaryTreatment.frequency}</span>
                  </div>
                )}

                {primaryTreatment.dosage && (
                  <div className="flex items-center gap-2 text-sm">
                    <Pill className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">{t('treatments.dosage')}:</span>
                    <span>{primaryTreatment.dosage}</span>
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <Stethoscope className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">{t('treatments.prescribedBy')}:</span>
                  <span>{primaryTreatment.doctor}</span>
                </div>


              </div>
            </div>



            <div className="pt-2">
              <div className="text-sm text-muted-foreground mb-1">{t('treatments.notes')}:</div>
              <p className="text-sm">{primaryTreatment.notes}</p>
            </div>
          </div>
        )}

        {/* Other active treatments */}
        {activeTreatments.length > 1 && (
          <>
            <Separator />
            <div>
              <h4 className="font-medium mb-3">{t('treatments.additionalTreatments')}</h4>
              <div className="space-y-3">
                {activeTreatments
                  .filter(t => t.id !== primaryTreatment?.id)
                  .map(treatment => (
                    <div key={treatment.id} className="flex items-center justify-between bg-slate-50 dark:bg-slate-800 p-3 rounded-md">
                      <div className="flex items-center gap-3">
                        <div>
                          {getTreatmentIcon(treatment.treatment_type || treatment.type)}
                        </div>
                        <div>
                          <div className="font-medium">{treatment.treatment_name || treatment.name}</div>
                          <div className="text-xs text-muted-foreground">
                            {treatment.treatment_type || treatment.type} • {format(new Date(treatment.start_date || treatment.startDate), 'PP')}
                            {treatment.frequency && ` • ${treatment.frequency}`}
                          </div>
                        </div>
                      </div>
                      <Badge variant={treatment.status?.toUpperCase() === 'ACTIVE' ? 'default' : 'outline'}>
                        {treatment.status}
                      </Badge>
                    </div>
                  ))
                }
              </div>
            </div>
          </>
        )}
      </CardContent>

    </Card>
  );
};

export default TreatmentPlan;
