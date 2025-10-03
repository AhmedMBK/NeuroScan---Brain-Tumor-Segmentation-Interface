import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  ArrowLeft,
  User,
  Mail,
  Phone,
  MapPin,
  Calendar,
  Activity,
  Heart,
  UserCircle,
  FileText,
  Pencil,
  Trash2,
  Clock,
  Building,
  Shield,
  Ruler,
  Weight
} from 'lucide-react';
import { Patient } from '@/services/api';
import { usePatient } from '@/hooks/usePatients';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';
import PatientTimeline from '@/components/PatientTimeline';
import SegmentationWorkflow from '@/components/SegmentationWorkflow';

// Helper function to calculate age
const calculateAge = (dateOfBirth: string): number => {
  const today = new Date();
  const birthDate = new Date(dateOfBirth);
  let age = today.getFullYear() - birthDate.getFullYear();
  const m = today.getMonth() - birthDate.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  return age;
};

// Helper function to get initials from name
const getInitials = (firstName: string, lastName: string): string => {
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
};

const PatientDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();

  // Utiliser l'API CereBloom
  const { data: patient, isLoading: loading, error } = usePatient(id || '');

  // Determine which view to show based on the URL
  const isEditMode = location.pathname.includes('/edit');
  const isScansMode = location.pathname.includes('/scans');

  // Gestion des erreurs
  if (error) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="text-center">
            <h2 className="text-2xl font-bold">Erreur de chargement</h2>
            <p className="text-muted-foreground mt-2">
              Impossible de charger les données du patient: {error.message}
            </p>
            <Button asChild className="mt-4">
              <Link to="/patients">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Retour
              </Link>
            </Button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (loading) {
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

  const age = calculateAge(patient.date_of_birth);

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
          <div className="flex items-center gap-2">
            <Button variant="outline" size="icon" asChild className="h-8 w-8">
              <Link to="/patients">
                <ArrowLeft className="h-4 w-4" />
              </Link>
            </Button>
            <h1 className="text-2xl font-bold tracking-tight">{t('patients.patientDetails')}</h1>
          </div>
          <div className="flex gap-2 mt-4 md:mt-0">
            <Button variant="outline" asChild>
              <Link to={`/patients/${patient.id}/edit`}>
                <Pencil className="mr-2 h-4 w-4" />
                {t('common.edit')}
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link to={`/patients/${patient.id}/exam-history`}>
                <FileText className="mr-2 h-4 w-4" />
                {t('scans.examHistory')}
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link to={`/patients/${patient.id}/treatment-tracking`}>
                <Activity className="mr-2 h-4 w-4" />
                {t('treatments.treatmentTracking')}
              </Link>
            </Button>
          </div>
        </div>

        {/* Patient Profile Card */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row gap-6">
              {/* Avatar and basic info */}
              <div className="flex flex-col items-center md:items-start gap-4">
                <Avatar className="h-24 w-24 border-2 border-slate-200 dark:border-slate-700">
                  <AvatarFallback className="text-2xl bg-medical/10 text-medical">
                    {getInitials(patient.first_name, patient.last_name)}
                  </AvatarFallback>
                </Avatar>
                <div className="text-center md:text-left">
                  <h2 className="text-2xl font-bold">
                    {patient.first_name} {patient.last_name}
                  </h2>
                  <div className="flex items-center gap-2 mt-1 text-muted-foreground">
                    <Badge variant="outline" className="bg-medical/10 text-medical border-medical/20">
                      ID: {patient.id}
                    </Badge>
                    <span>•</span>
                    <span>{age} ans</span>
                    <span>•</span>
                    <span>{patient.gender === 'MALE' ? 'Homme' : 'Femme'}</span>
                  </div>
                </div>
              </div>

              {/* Contact information */}
              <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 md:mt-0">
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">{patient.email || 'Non renseigné'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Phone className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">{patient.phone || 'Non renseigné'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">{patient.address || 'Non renseignée'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">
                      Date de naissance: {new Date(patient.date_of_birth).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Heart className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">
                      Groupe sanguin: {patient.blood_type || 'Non renseigné'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Ruler className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">
                      Taille: {patient.height ? `${patient.height} cm` : 'Non renseignée'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Weight className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">
                      Poids: {patient.weight ? `${patient.weight} kg` : 'Non renseigné'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <UserCircle className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">
                      Médecin assigné: À définir
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Key stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-slate-200 dark:border-slate-700">
              <div className="bg-slate-50 dark:bg-slate-800 p-3 rounded-lg">
                <div className="text-xs text-muted-foreground mb-1">Créé le</div>
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-medical" />
                  <span className="font-medium">{new Date(patient.created_at).toLocaleDateString()}</span>
                </div>
              </div>

              <div className="bg-slate-50 dark:bg-slate-800 p-3 rounded-lg">
                <div className="text-xs text-muted-foreground mb-1">Dernière mise à jour</div>
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-medical" />
                  <span className="font-medium">{new Date(patient.updated_at).toLocaleDateString()}</span>
                </div>
              </div>

              <div className="bg-slate-50 dark:bg-slate-800 p-3 rounded-lg">
                <div className="text-xs text-muted-foreground mb-1">Prochain RDV</div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-medical" />
                  <span className="font-medium">À planifier</span>
                </div>
              </div>

              <div className="bg-slate-50 dark:bg-slate-800 p-3 rounded-lg">
                <div className="text-xs text-muted-foreground mb-1">Statut</div>
                <div className="flex items-center gap-2">
                  <Shield className="h-4 w-4 text-medical" />
                  <Badge variant="default" className="bg-green-100 text-green-800">Actif</Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Emergency Contact */}
        {patient.emergency_contact && (
          <Card className="mb-6">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center gap-2">
                <Phone className="h-5 w-5 text-red-500" />
                Contact d'urgence
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <div className="text-sm text-muted-foreground">Nom</div>
                  <div className="font-medium">{patient.emergency_contact.name || 'Non renseigné'}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Relation</div>
                  <div className="font-medium">{patient.emergency_contact.relationship || 'Non renseignée'}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Téléphone</div>
                  <div className="font-medium">{patient.emergency_contact.phone || 'Non renseigné'}</div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Conditional content based on mode */}
        {isEditMode ? (
          <Card>
            <CardHeader>
              <CardTitle>{t('patients.editPatient')}</CardTitle>
              <CardDescription>{t('patients.editPatientDescription')}</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">{t('common.comingSoon')}</p>
              {/* Patient edit form would go here */}
            </CardContent>
          </Card>
        ) : isScansMode ? (
          <Card>
            <CardHeader>
              <CardTitle>{t('navigation.scans')}</CardTitle>
              <CardDescription>{t('scans.patientScansDescription')}</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">{t('common.comingSoon')}</p>
              {/* Patient scans would go here */}
            </CardContent>
          </Card>
        ) : (
          /* Default view - Tabs for Medical Info, Segmentation and Timeline */
          <Tabs defaultValue="segmentation" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="segmentation">🧠 {t('segmentation.aiSegmentation')}</TabsTrigger>
              <TabsTrigger value="medical-info">{t('patients.medicalInformation')}</TabsTrigger>
              <TabsTrigger value="timeline">{t('patients.timeline')}</TabsTrigger>
            </TabsList>
            <TabsContent value="segmentation" className="mt-6">
              <SegmentationWorkflow
                patientId={patient.id}
                patientName={`${patient.first_name} ${patient.last_name}`}
              />
            </TabsContent>
            <TabsContent value="medical-info" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>{t('patients.medicalInformation')}</CardTitle>
                  <CardDescription>
                    {t('patients.medicalHistoryDescription')}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium mb-2">{t('patients.medicalHistory')}</h4>
                      <p className="text-muted-foreground">
                        {patient.medical_history ?
                          JSON.stringify(patient.medical_history) :
                          t('patients.noMedicalHistory')
                        }
                      </p>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">{t('patients.notes')}</h4>
                      <p className="text-muted-foreground">
                        {patient.notes || t('patients.noNotes')}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="timeline" className="mt-6">
              <PatientTimeline
                patientId={patient.id}
                patientCreatedAt={patient.created_at}
              />
            </TabsContent>
          </Tabs>
        )}
      </div>
    </DashboardLayout>
  );
};

export default PatientDetail;
