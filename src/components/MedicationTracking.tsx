import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';
import {
  Pill,
  Clock,
  Calendar,
  AlertCircle,
  CheckCircle,
  Plus,
  Trash2,
  Edit,
  Zap,
  MoreHorizontal
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
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';

interface MedicationTrackingProps {
  patientId?: string;
}

const MedicationTracking: React.FC<MedicationTrackingProps> = ({ patientId }) => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<string>('current');

  // Récupérer les traitements depuis l'API
  const { data: treatments = [], isLoading, error } = useTreatments(patientId);

  // Filter medication treatments
  const medicationTreatments = treatments.filter((treatment: any) =>
    treatment.treatment_type?.toLowerCase().includes('medication') ||
    treatment.medication_name
  );

  // Current medications
  const currentMedications = medicationTreatments.filter(treatment =>
    treatment.status === 'Active'
  );

  // Past medications
  const pastMedications = medicationTreatments.filter(treatment =>
    treatment.status === 'Completed' || treatment.status === 'Cancelled'
  );

  // Sort medications by start date (newest first)
  const sortedCurrentMedications = [...currentMedications].sort((a, b) =>
    new Date(b.startDate).getTime() - new Date(a.startDate).getTime()
  );

  const sortedPastMedications = [...pastMedications].sort((a, b) =>
    new Date(b.startDate).getTime() - new Date(a.startDate).getTime()
  );

  if (medicationTreatments.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t('medications.medicationTracking')}</CardTitle>
          <CardDescription>{t('medications.medicationTrackingDescription')}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center py-10">
          <Pill className="h-10 w-10 text-muted-foreground mb-4" />
          <p className="text-muted-foreground">{t('medications.noMedications')}</p>
        </CardContent>
        <CardFooter>
          <Button className="w-full">
            <Plus className="mr-2 h-4 w-4" />
            {t('medications.addMedication')}
          </Button>
        </CardFooter>
      </Card>
    );
  }

  // Function to render medication card
  const renderMedicationCard = (medication: Treatment) => (
    <Card key={medication.id} className="overflow-hidden">
      <div className="bg-medical/10 dark:bg-medical/20 px-4 py-2 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Pill className="h-4 w-4 text-medical" />
          <h4 className="font-medium">{medication.name}</h4>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>
              <Edit className="mr-2 h-4 w-4" />
              <span>{t('common.edit')}</span>
            </DropdownMenuItem>
            <DropdownMenuItem>
              <CheckCircle className="mr-2 h-4 w-4" />
              <span>{t('medications.markAsTaken')}</span>
            </DropdownMenuItem>
            <DropdownMenuItem className="text-red-500">
              <Trash2 className="mr-2 h-4 w-4" />
              <span>{t('common.delete')}</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      <CardContent className="p-4">
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">{t('medications.frequency')}:</span>
            </div>
            <div>{medication.frequency || t('common.notSpecified')}</div>

            <div className="flex items-center gap-2">
              <Pill className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">{t('medications.dosage')}:</span>
            </div>
            <div>{medication.dosage || t('common.notSpecified')}</div>

            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">{t('medications.startDate')}:</span>
            </div>
            <div>{format(new Date(medication.startDate), 'PP')}</div>

            {medication.endDate && (
              <>
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">{t('medications.endDate')}:</span>
                </div>
                <div>{format(new Date(medication.endDate), 'PP')}</div>
              </>
            )}
          </div>

          {medication.sideEffects.length > 0 && (
            <div className="pt-2 mt-2 border-t">
              <div className="text-sm text-muted-foreground mb-1">{t('medications.reportedSideEffects')}:</div>
              <div className="flex flex-wrap gap-1">
                {medication.sideEffects.map((effect, index) => (
                  <Badge key={index} variant="outline" className="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 border-red-200 dark:border-red-800">
                    {effect}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {medication.status === 'Active' && (
            <div className="pt-2 mt-2 border-t">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-muted-foreground">{t('medications.adherence')}</span>
                <span className="font-medium">85%</span>
              </div>
              <Progress value={85} className="h-2" />
            </div>
          )}

          {medication.status === 'Completed' && (
            <div className="pt-2 mt-2 border-t">
              <div className="flex items-center gap-2 text-sm">
                <Zap className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">{t('medications.effectiveness')}:</span>
                <span>{medication.effectiveness}</span>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('medications.medicationTracking')}</CardTitle>
        <CardDescription>{t('medications.medicationTrackingDescription')}</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-4">
            <TabsTrigger value="current" className="flex items-center gap-2">
              <Pill className="h-4 w-4" />
              <span>{t('medications.currentMedications')}</span>
            </TabsTrigger>
            <TabsTrigger value="past" className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              <span>{t('medications.pastMedications')}</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="current">
            {sortedCurrentMedications.length === 0 ? (
              <div className="text-center py-6">
                <p className="text-muted-foreground">{t('medications.noCurrentMedications')}</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {sortedCurrentMedications.map(medication => renderMedicationCard(medication))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="past">
            {sortedPastMedications.length === 0 ? (
              <div className="text-center py-6">
                <p className="text-muted-foreground">{t('medications.noPastMedications')}</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {sortedPastMedications.map(medication => renderMedicationCard(medication))}
              </div>
            )}
          </TabsContent>
        </Tabs>

        {/* Medication schedule */}
        <div className="mt-6 pt-4 border-t">
          <h3 className="font-medium mb-3">{t('medications.todaySchedule')}</h3>

          {currentMedications.length === 0 ? (
            <div className="text-center py-4">
              <p className="text-muted-foreground">{t('medications.noMedicationsScheduled')}</p>
            </div>
          ) : (
            <div className="space-y-3">
              {currentMedications.map(medication => (
                <div key={medication.id} className="flex items-center justify-between p-3 rounded-md bg-slate-50 dark:bg-slate-800">
                  <div className="flex items-center gap-3">
                    <div>
                      <Pill className="h-5 w-5 text-medical" />
                    </div>
                    <div>
                      <div className="font-medium">{medication.name}</div>
                      <div className="text-xs text-muted-foreground">
                        {medication.dosage} • {medication.frequency}
                      </div>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    <CheckCircle className="mr-2 h-4 w-4" />
                    {t('medications.markAsTaken')}
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Side effects reporting */}
        <div className="mt-6 pt-4 border-t">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium">{t('medications.sideEffectsReporting')}</h3>
            <Button variant="outline" size="sm">
              <AlertCircle className="mr-2 h-4 w-4" />
              {t('medications.reportSideEffect')}
            </Button>
          </div>

          <Card className="bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800">
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-amber-500 mt-0.5" />
                <div>
                  <h4 className="font-medium text-amber-700 dark:text-amber-300">
                    {t('medications.sideEffectsImportance')}
                  </h4>
                  <p className="text-sm text-amber-600 dark:text-amber-400 mt-1">
                    {t('medications.sideEffectsDescription')}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </CardContent>
      <CardFooter>
        <Button className="w-full">
          <Plus className="mr-2 h-4 w-4" />
          {t('medications.addMedication')}
        </Button>
      </CardFooter>
    </Card>
  );
};

export default MedicationTracking;
