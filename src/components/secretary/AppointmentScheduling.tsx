import React, { useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { format, addDays, startOfWeek, endOfWeek, eachDayOfInterval, isSameDay } from 'date-fns';
import { fr } from 'date-fns/locale';
import { 
  Calendar,
  Plus,
  Clock,
  User,
  ChevronLeft,
  ChevronRight,
  Filter,
  Search,
  MoreHorizontal,
  Edit,
  Trash2,
  Phone,
  Mail
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { useAppointments, useCreateAppointment } from '@/hooks/api/useAppointments';
import { usePatientsForSelect } from '@/hooks/usePatients';
import { useDoctors } from '@/hooks/api/useDoctors';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';

const AppointmentScheduling: React.FC = () => {
  const { t } = useTranslation();
  const { userData } = useAuth();
  const { toast } = useToast();
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [viewMode, setViewMode] = useState<'day' | 'week' | 'list'>('week');
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  // États pour le formulaire de création
  const [formData, setFormData] = useState({
    patient_id: '',
    appointment_date: '',
    appointment_time: '',
    appointment_type: '',
    notes: ''
  });

  // Récupérer automatiquement le médecin assigné à la secrétaire
  const assignedDoctorId = userData?.assigned_doctor_id;



  // Hooks pour récupérer les données
  const { data: appointmentsData, isLoading, error } = useAppointments();
  const { data: patients, isLoading: patientsLoading } = usePatientsForSelect();
  const { data: doctorsData, isLoading: doctorLoading } = useDoctors();
  const createAppointmentMutation = useCreateAppointment();

  // Trouver le médecin assigné dans la liste (avec vérification de sécurité)
  const assignedDoctorInfo = useMemo(() => {
    if (!doctorsData || !Array.isArray(doctorsData) || !assignedDoctorId) {
      return null;
    }
    return doctorsData.find((doc: any) => doc.id === assignedDoctorId);
  }, [doctorsData, assignedDoctorId]);

  // Filtrer les rendez-vous selon la vue
  const getFilteredAppointments = () => {
    if (!appointmentsData) return [];

    let filtered = appointmentsData.filter((apt: any) => {
      const patientName = apt.patient ? `${apt.patient.first_name} ${apt.patient.last_name}` : '';
      const matchesSearch =
        patientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        apt.appointment_type?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        apt.notes?.toLowerCase().includes(searchTerm.toLowerCase());

      return matchesSearch;
    });

    if (viewMode === 'day') {
      filtered = filtered.filter((apt: any) => 
        isSameDay(new Date(apt.appointment_date), selectedDate)
      );
    } else if (viewMode === 'week') {
      const weekStart = startOfWeek(selectedDate, { locale: fr });
      const weekEnd = endOfWeek(selectedDate, { locale: fr });
      filtered = filtered.filter((apt: any) => {
        const aptDate = new Date(apt.appointment_date);
        return aptDate >= weekStart && aptDate <= weekEnd;
      });
    }

    return filtered.sort((a: any, b: any) => 
      new Date(a.appointment_date).getTime() - new Date(b.appointment_date).getTime()
    );
  };

  const filteredAppointments = getFilteredAppointments();

  // Navigation des dates
  const navigateDate = (direction: 'prev' | 'next') => {
    if (viewMode === 'day') {
      setSelectedDate(prev => addDays(prev, direction === 'next' ? 1 : -1));
    } else if (viewMode === 'week') {
      setSelectedDate(prev => addDays(prev, direction === 'next' ? 7 : -7));
    }
  };

  // Gestion du formulaire de création
  const handleFormChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const resetForm = () => {
    setFormData({
      patient_id: '',
      appointment_date: '',
      appointment_time: '',
      appointment_type: '',
      notes: ''
    });
  };

  const handleCreateAppointment = async () => {
    // Validation basique
    if (!formData.patient_id || !assignedDoctorId || !formData.appointment_date || !formData.appointment_time) {
      toast({
        title: "Erreur",
        description: "Veuillez remplir tous les champs obligatoires",
        variant: "destructive",
      });
      return;
    }

    // Vérifier que la secrétaire a un médecin assigné
    if (!assignedDoctorId) {
      toast({
        title: "Erreur",
        description: "Aucun médecin assigné à votre compte. Contactez l'administrateur.",
        variant: "destructive",
      });
      return;
    }

    try {
      await createAppointmentMutation.mutateAsync({
        patient_id: formData.patient_id,
        doctor_id: assignedDoctorId,
        appointment_date: formData.appointment_date,
        appointment_time: formData.appointment_time,
        appointment_type: formData.appointment_type || 'CONSULTATION',
        notes: formData.notes,
        status: 'SCHEDULED'
      });

      // Fermer le dialog et réinitialiser le formulaire
      setIsCreateDialogOpen(false);
      resetForm();
    } catch (error) {
      console.error('Erreur lors de la création du rendez-vous:', error);
    }
  };

  // Obtenir le statut du rendez-vous
  const getAppointmentStatus = (appointment: any) => {
    const now = new Date();
    const aptDate = new Date(appointment.appointment_date);
    
    if (aptDate < now) {
      return { label: 'Passé', variant: 'secondary' as const };
    } else if (aptDate.toDateString() === now.toDateString()) {
      return { label: 'Aujourd\'hui', variant: 'default' as const };
    } else {
      return { label: 'À venir', variant: 'outline' as const };
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Planning des Rendez-vous
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-medical mx-auto mb-4"></div>
              <p className="text-muted-foreground">Chargement du planning...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Planning des Rendez-vous
            </CardTitle>
            <CardDescription>
              Gérer les rendez-vous de votre médecin
            </CardDescription>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Nouveau RDV
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-lg max-h-[80vh] overflow-hidden flex flex-col">
              <DialogHeader>
                <DialogTitle>Planifier un nouveau rendez-vous</DialogTitle>
                <DialogDescription>
                  Créer un rendez-vous pour un patient
                </DialogDescription>
              </DialogHeader>

              <div className="flex-1 overflow-y-auto px-1">
                <div className="space-y-6 py-4">
                {/* Sélection du patient */}
                <div className="space-y-2">
                  <Label htmlFor="patient">Patient *</Label>
                  <Select
                    value={formData.patient_id}
                    onValueChange={(value) => handleFormChange('patient_id', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Sélectionner un patient" />
                    </SelectTrigger>
                    <SelectContent>
                      {patientsLoading ? (
                        <SelectItem value="loading" disabled>Chargement des patients...</SelectItem>
                      ) : patients && patients.length > 0 ? (
                        patients.map((patient: any) => (
                          <SelectItem key={patient.value} value={patient.value}>
                            {patient.label}
                            {patient.email && <span className="text-muted-foreground ml-2">({patient.email})</span>}
                          </SelectItem>
                        ))
                      ) : (
                        <SelectItem value="empty" disabled>Aucun patient disponible</SelectItem>
                      )}
                    </SelectContent>
                  </Select>
                </div>

                {/* Date du rendez-vous */}
                <div className="space-y-2">
                  <Label htmlFor="date">Date *</Label>
                  <Input
                    type="date"
                    value={formData.appointment_date}
                    onChange={(e) => handleFormChange('appointment_date', e.target.value)}
                    min={new Date().toISOString().split('T')[0]}
                  />
                </div>

                {/* Heure du rendez-vous */}
                <div className="space-y-2">
                  <Label htmlFor="time">Heure *</Label>
                  <Select
                    value={formData.appointment_time}
                    onValueChange={(value) => handleFormChange('appointment_time', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Sélectionner une heure" />
                    </SelectTrigger>
                    <SelectContent>
                      {['08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
                        '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30',
                        '16:00', '16:30', '17:00', '17:30', '18:00'].map((time) => (
                        <SelectItem key={time} value={time}>
                          {time}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Type de rendez-vous */}
                <div className="space-y-2">
                  <Label htmlFor="type">Type de rendez-vous</Label>
                  <Select
                    value={formData.appointment_type}
                    onValueChange={(value) => handleFormChange('appointment_type', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Sélectionner un type" />
                    </SelectTrigger>
                    <SelectContent>
                      {['CONSULTATION', 'SUIVI', 'CONTROLE', 'URGENCE', 'PREMIERE_CONSULTATION',
                        'CONSULTATION_RESULTATS', 'PRE_OPERATOIRE', 'POST_OPERATOIRE'].map((type) => (
                        <SelectItem key={type} value={type}>
                          {type.replace(/_/g, ' ')}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Notes */}
                <div className="space-y-2">
                  <Label htmlFor="notes">Notes</Label>
                  <Textarea
                    placeholder="Notes additionnelles..."
                    value={formData.notes}
                    onChange={(e) => handleFormChange('notes', e.target.value)}
                    rows={3}
                  />
                </div>

                {/* Boutons d'action */}
                <div className="flex justify-end gap-3 pt-4">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setIsCreateDialogOpen(false);
                      resetForm();
                    }}
                  >
                    Annuler
                  </Button>
                  <Button
                    onClick={handleCreateAppointment}
                    disabled={createAppointmentMutation.isPending}
                  >
                    {createAppointmentMutation.isPending ? 'Création...' : 'Créer le rendez-vous'}
                  </Button>
                </div>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent>
        {/* Contrôles de navigation et vue */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigateDate('prev')}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <div className="text-lg font-semibold min-w-[200px] text-center">
                {viewMode === 'day' 
                  ? format(selectedDate, 'EEEE dd MMMM yyyy', { locale: fr })
                  : viewMode === 'week'
                  ? `${format(startOfWeek(selectedDate, { locale: fr }), 'dd MMM', { locale: fr })} - ${format(endOfWeek(selectedDate, { locale: fr }), 'dd MMM yyyy', { locale: fr })}`
                  : 'Tous les rendez-vous'
                }
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigateDate('next')}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant={viewMode === 'day' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('day')}
            >
              Jour
            </Button>
            <Button
              variant={viewMode === 'week' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('week')}
            >
              Semaine
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('list')}
            >
              Liste
            </Button>
          </div>
        </div>

        {/* Statistiques rapides */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {filteredAppointments.length}
            </div>
            <div className="text-sm text-blue-600">
              {viewMode === 'day' ? 'Aujourd\'hui' : viewMode === 'week' ? 'Cette semaine' : 'Total'}
            </div>
          </div>
          <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {filteredAppointments.filter(apt => 
                isSameDay(new Date(apt.appointment_date), new Date())
              ).length}
            </div>
            <div className="text-sm text-green-600">Aujourd'hui</div>
          </div>
          <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">
              {filteredAppointments.filter(apt => 
                new Date(apt.appointment_date) > new Date()
              ).length}
            </div>
            <div className="text-sm text-orange-600">À venir</div>
          </div>
          <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {filteredAppointments.filter(apt => 
                new Date(apt.appointment_date) < new Date()
              ).length}
            </div>
            <div className="text-sm text-purple-600">Passés</div>
          </div>
        </div>

        {/* Recherche */}
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Rechercher un rendez-vous..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Liste des rendez-vous */}
        <div className="border rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Patient</TableHead>
                <TableHead>Date & Heure</TableHead>
                <TableHead>Motif</TableHead>
                <TableHead>Statut</TableHead>
                <TableHead>Contact</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAppointments.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8">
                    <div className="text-muted-foreground">
                      {searchTerm 
                        ? 'Aucun rendez-vous trouvé avec ces critères'
                        : 'Aucun rendez-vous pour cette période'
                      }
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                filteredAppointments.map((appointment: any) => {
                  const status = getAppointmentStatus(appointment);
                  return (
                    <TableRow key={appointment.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <div className="h-8 w-8 rounded-full bg-blue-100 dark:bg-blue-800 flex items-center justify-center">
                            <User className="h-4 w-4 text-blue-600" />
                          </div>
                          <div>
                            <div className="font-medium">
                              {appointment.patient ? `${appointment.patient.first_name} ${appointment.patient.last_name}` : 'Patient Inconnu'}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              ID: {appointment.patient_id?.slice(0, 8)}...
                            </div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          <div className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            {format(new Date(appointment.appointment_date), 'dd/MM/yyyy', { locale: fr })}
                          </div>
                          <div className="flex items-center gap-1 text-sm text-muted-foreground">
                            <Clock className="h-3 w-3" />
                            {appointment.appointment_time}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">
                          {appointment.appointment_type || 'Consultation'}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={status.variant}>
                          {status.label}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          {appointment.patient_email && (
                            <div className="text-sm flex items-center gap-1">
                              <Mail className="h-3 w-3" />
                              {appointment.patient_email}
                            </div>
                          )}
                          {appointment.patient_phone && (
                            <div className="text-sm flex items-center gap-1">
                              <Phone className="h-3 w-3" />
                              {appointment.patient_phone}
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Actions</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem>
                              <Edit className="mr-2 h-4 w-4" />
                              Modifier
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Phone className="mr-2 h-4 w-4" />
                              Appeler patient
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem className="text-destructive">
                              <Trash2 className="mr-2 h-4 w-4" />
                              Annuler
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
};

export default AppointmentScheduling;
