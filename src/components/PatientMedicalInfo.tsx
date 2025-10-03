import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  AlertCircle,
  Heart,
  Scissors,
  Users,
  Activity,
  Pill,
  FileText
} from 'lucide-react';
import { Patient } from '@/data/mockPatients';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

interface PatientMedicalInfoProps {
  patient: Patient;
}

const PatientMedicalInfo: React.FC<PatientMedicalInfoProps> = ({ patient }) => {
  const { t } = useTranslation();

  return (
    <div className="space-y-6">
      {/* Allergies */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-md flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-red-500" />
            {t('patients.allergies')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {patient.medicalHistory.allergies.length === 0 ? (
            <p className="text-muted-foreground text-sm">{t('patients.noAllergies')}</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {patient.medicalHistory.allergies.map((allergy, index) => (
                <Badge key={index} variant="outline" className="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 border-red-200 dark:border-red-800">
                  {allergy}
                </Badge>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Chronic Conditions */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-md flex items-center gap-2">
            <Activity className="h-5 w-5 text-amber-500" />
            {t('patients.chronicConditions')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {patient.medicalHistory.chronicConditions.length === 0 ? (
            <p className="text-muted-foreground text-sm">{t('patients.noChronicConditions')}</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {patient.medicalHistory.chronicConditions.map((condition, index) => (
                <Badge key={index} variant="outline" className="bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800">
                  {condition}
                </Badge>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Past Surgeries */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-md flex items-center gap-2">
            <Scissors className="h-5 w-5 text-blue-500" />
            {t('patients.pastSurgeries')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {patient.medicalHistory.pastSurgeries.length === 0 ? (
            <p className="text-muted-foreground text-sm">{t('patients.noPastSurgeries')}</p>
          ) : (
            <div className="space-y-3">
              {patient.medicalHistory.pastSurgeries.map((surgery, index) => (
                <div key={index} className="bg-slate-50 dark:bg-slate-800 p-3 rounded-md">
                  <div className="flex justify-between items-start">
                    <h4 className="font-medium text-slate-900 dark:text-white">{surgery.procedure}</h4>
                    <span className="text-xs text-slate-500 dark:text-slate-400">
                      {new Date(surgery.date).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 dark:text-slate-300 mt-1">{surgery.notes}</p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Family History */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-md flex items-center gap-2">
            <Users className="h-5 w-5 text-indigo-500" />
            {t('patients.familyHistory')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {patient.medicalHistory.familyHistory.length === 0 ? (
            <p className="text-muted-foreground text-sm">{t('patients.noFamilyHistory')}</p>
          ) : (
            <div className="space-y-1">
              {patient.medicalHistory.familyHistory.map((history, index) => (
                <div key={index} className="flex items-center gap-2">
                  <Heart className="h-4 w-4 text-indigo-400" />
                  <span className="text-sm">{history}</span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Current Medications */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-md flex items-center gap-2">
            <Pill className="h-5 w-5 text-green-500" />
            {t('patients.currentMedications')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* This is a placeholder - we would need to get active medications from treatments */}
          <p className="text-muted-foreground text-sm">{t('patients.noCurrentMedications')}</p>
        </CardContent>
      </Card>

      {/* Notes */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-md flex items-center gap-2">
            <FileText className="h-5 w-5 text-slate-500" />
            {t('patients.notes')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm">{patient.notes || t('patients.noNotes')}</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default PatientMedicalInfo;
