import React, { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  ArrowLeft,
  FileText,
  Activity,
  Plus,
  Clipboard,
  History,
  Brain,
  Calendar
} from 'lucide-react';
import { usePatient } from '@/hooks/usePatients';
import { useTreatments } from '@/hooks/api/useTreatments';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import TreatmentPlan from '@/components/TreatmentPlan';
import TreatmentHistory from '@/components/TreatmentHistory';
import AppointmentCalendar from '@/components/AppointmentCalendar';
import CreateTreatmentModal from '@/components/CreateTreatmentModal';

const PatientTreatmentTracking: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [activeTab, setActiveTab] = useState<string>('plan');
  const [showCreateTreatment, setShowCreateTreatment] = useState(false);

  // Utiliser les vraies API
  const { data: patient, isLoading, error } = usePatient(id || '');

  // Récupérer les traitements du patient
  const { data: treatments = [] } = useTreatments(id);



  if (error) {
    toast({
      variant: 'destructive',
      title: t('common.error'),
      description: t('patients.patientNotFound'),
    });
    navigate('/patients');
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-medical"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (!patient) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="text-center">
            <h2 className="text-2xl font-bold">{t('patients.patientNotFound')}</h2>
            <p className="text-muted-foreground mt-2">{t('patients.patientNotFoundDescription')}</p>
            <Button asChild className="mt-4">
              <Link to="/patients">
                <ArrowLeft className="mr-2 h-4 w-4" />
                {t('common.back')}
              </Link>
            </Button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  // Count active treatments
  const activeTreatments = treatments.filter(treatment =>
    treatment.status?.toUpperCase() === 'ACTIVE' || treatment.status?.toUpperCase() === 'SCHEDULED'
  ).length;



  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
          <div className="flex items-center gap-2">
            <Button variant="outline" size="icon" asChild className="h-8 w-8">
              <Link to={`/patients/${patient.id}`}>
                <ArrowLeft className="h-4 w-4" />
              </Link>
            </Button>
            <h1 className="text-2xl font-bold tracking-tight">{t('treatments.treatmentTracking')}</h1>
          </div>
          <div className="flex gap-2 mt-4 md:mt-0">
            <Button variant="outline" asChild>
              <Link to={`/patients/${patient.id}`}>
                <FileText className="mr-2 h-4 w-4" />
                {t('patients.patientDetails')}
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link to={`/patients/${patient.id}/exam-history`}>
                <Brain className="mr-2 h-4 w-4" />
                {t('scans.examHistory')}
              </Link>
            </Button>
            <Button onClick={() => setShowCreateTreatment(true)}>
              <Plus className="mr-2 h-4 w-4" />
              {t('treatments.addTreatment')}
            </Button>
          </div>
        </div>

        {/* Patient Info Card */}
        <Card className="mb-6">
          <CardContent className="p-4">
            <div className="flex items-center gap-4">
              <div className="h-10 w-10 rounded-full bg-medical/10 flex items-center justify-center">
                <Activity className="h-5 w-5 text-medical" />
              </div>
              <div>
                <h2 className="font-semibold">
                  {patient.first_name} {patient.last_name}
                </h2>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Badge variant="outline" className="bg-medical/10 text-medical border-medical/20">
                    ID: {patient.id}
                  </Badge>
                  <span>•</span>
                  <span>{t('treatments.activeTreatments')}: {activeTreatments}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>



        {/* Tabs for different views */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="plan" className="flex items-center gap-2">
              <Clipboard className="h-4 w-4" />
              <span>{t('treatments.plan')}</span>
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center gap-2">
              <History className="h-4 w-4" />
              <span>{t('treatments.history')}</span>
            </TabsTrigger>
            <TabsTrigger value="appointments" className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              <span>{t('appointments.appointments')}</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="plan" className="mt-6">
            <TreatmentPlan patientId={id} />
          </TabsContent>

          <TabsContent value="history" className="mt-6">
            <TreatmentHistory patientId={id} />
          </TabsContent>

          <TabsContent value="appointments" className="mt-6">
            <AppointmentCalendar patientId={id} />
          </TabsContent>
        </Tabs>



        {/* Modal de création de traitement */}
        <CreateTreatmentModal
          isOpen={showCreateTreatment}
          onClose={() => setShowCreateTreatment(false)}
          patientId={patient.id}
          patientName={`${patient.first_name} ${patient.last_name}`}
        />
      </div>
    </DashboardLayout>
  );
};

export default PatientTreatmentTracking;
