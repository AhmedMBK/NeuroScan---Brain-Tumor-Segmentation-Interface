import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';
import {
  Stethoscope,
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  Edit,
  Trash2,
  UserCheck,
  UserX,
  Mail,
  Phone,
  Calendar,
  Award
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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useDoctors, useDoctorsStats } from '@/hooks/useDoctors';
import RoleBasedAccess from '@/components/common/RoleBasedAccess';

interface DoctorManagementProps {
  onCreateDoctor: () => void;
  onEditDoctor: (doctorId: string) => void;
  showCreateButton?: boolean;
}

const DoctorManagement: React.FC<DoctorManagementProps> = ({ onCreateDoctor, onEditDoctor, showCreateButton = true }) => {
  const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState('');

  // Hooks API
  const { data: doctorsResponse, isLoading, error } = useDoctors();
  const { data: doctorsStats } = useDoctorsStats();

  // Extraire le tableau de médecins (gérer les réponses paginées ou directes)
  const doctors = Array.isArray(doctorsResponse)
    ? doctorsResponse
    : (doctorsResponse?.items || doctorsResponse?.data || []);

  // Debug temporaire
  console.log('DoctorManagement - doctorsResponse:', doctorsResponse);
  console.log('DoctorManagement - doctors:', doctors);
  console.log('DoctorManagement - isArray:', Array.isArray(doctors));

  // Filtrage des médecins (avec vérification de sécurité)
  const filteredDoctors = Array.isArray(doctors) ? doctors.filter((doctor: any) => {
    const matchesSearch =
      doctor.user?.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doctor.user?.last_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doctor.user?.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doctor.bio?.toLowerCase().includes(searchTerm.toLowerCase());

    // Pas de filtrage par spécialité car ce champ n'existe plus
    return matchesSearch;
  }) : [];

  // Plus de spécialités car ce champ n'existe plus dans la DB
  const specialties: string[] = [];

  // Obtenir le statut médecin
  const getDoctorStatus = (doctor: any) => {
    return doctor.is_active !== false ? 'Actif' : 'Inactif';
  };

  // Fonction supprimée car les spécialités n'existent plus dans la DB

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Stethoscope className="h-5 w-5" />
            Gestion des Médecins
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-medical mx-auto mb-4"></div>
              <p className="text-muted-foreground">Chargement des médecins...</p>
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
          <CardTitle className="flex items-center gap-2">
            <Stethoscope className="h-5 w-5" />
            Gestion des Médecins
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="h-8 w-8 text-destructive mx-auto mb-4">⚠️</div>
              <p className="text-destructive">Erreur lors du chargement des médecins</p>
              <p className="text-sm text-muted-foreground mt-2">
                {error instanceof Error ? error.message : 'Erreur inconnue'}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Données reçues: {JSON.stringify(doctorsResponse)}
              </p>
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
              <Stethoscope className="h-5 w-5" />
              Gestion des Médecins
            </CardTitle>
            <CardDescription>
              Gérer les profils médicaux, spécialités et informations professionnelles
            </CardDescription>
          </div>
          {showCreateButton && (
            <RoleBasedAccess allowedRoles={['ADMIN']}>
              <Button onClick={onCreateDoctor}>
                <Plus className="mr-2 h-4 w-4" />
                Nouveau Médecin
              </Button>
            </RoleBasedAccess>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {/* Filtres et recherche */}
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Rechercher un médecin..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Filtre par spécialité supprimé car ce champ n'existe plus */}
        </div>

        {/* Statistiques rapides */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{doctorsStats?.total_doctors || 0}</div>
            <div className="text-sm text-blue-600">Total Médecins</div>
          </div>
          <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{doctorsStats?.completed_profiles || 0}</div>
            <div className="text-sm text-green-600">Profils Complétés</div>
          </div>
          <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">{doctorsStats?.active_doctors || 0}</div>
            <div className="text-sm text-purple-600">Actifs</div>
          </div>
          <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">{doctorsStats?.pending_profiles || 0}</div>
            <div className="text-sm text-orange-600">En Attente</div>
          </div>
        </div>

        {/* Table des médecins */}
        <div className="border rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Médecin</TableHead>
                <TableHead>Bureau</TableHead>
                <TableHead>Contact</TableHead>
                <TableHead>Statut</TableHead>
                <TableHead>Créé le</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredDoctors.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8">
                    <div className="text-muted-foreground">
                      {searchTerm
                        ? 'Aucun médecin trouvé avec ces critères'
                        : 'Aucun médecin dans le système'
                      }
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                filteredDoctors.map((doctor: any) => (
                  <TableRow key={doctor.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <div className="h-8 w-8 rounded-full bg-medical/10 flex items-center justify-center">
                          <Stethoscope className="h-4 w-4 text-medical" />
                        </div>
                        <div>
                          <div className="font-medium">
                            Dr. {doctor.user?.first_name || doctor.first_name} {doctor.user?.last_name || doctor.last_name}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {doctor.user?.employee_id || 'ID non renseigné'}
                          </div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {doctor.office_location || 'Bureau non spécifié'}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="text-sm flex items-center gap-1">
                          <Mail className="h-3 w-3 text-muted-foreground" />
                          {doctor.user?.email || doctor.email || 'Non renseigné'}
                        </div>
                        <div className="text-sm flex items-center gap-1">
                          <Phone className="h-3 w-3 text-muted-foreground" />
                          {doctor.user?.phone || doctor.phone || 'Non renseigné'}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getDoctorStatus(doctor) === 'Actif' ? 'default' : 'secondary'}>
                        {getDoctorStatus(doctor)}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {doctor.created_at ? format(new Date(doctor.created_at), 'dd/MM/yyyy') : 'N/A'}
                    </TableCell>
                    <TableCell className="text-right">
                      <RoleBasedAccess allowedRoles={['ADMIN']}>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Actions</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem onClick={() => onEditDoctor(doctor.id)}>
                              <Edit className="mr-2 h-4 w-4" />
                              Modifier
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Calendar className="mr-2 h-4 w-4" />
                              Voir planning
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem>
                              {getDoctorStatus(doctor) === 'Actif' ? (
                                <>
                                  <UserX className="mr-2 h-4 w-4" />
                                  Désactiver
                                </>
                              ) : (
                                <>
                                  <UserCheck className="mr-2 h-4 w-4" />
                                  Activer
                                </>
                              )}
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem className="text-destructive">
                              <Trash2 className="mr-2 h-4 w-4" />
                              Supprimer
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </RoleBasedAccess>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
};

export default DoctorManagement;
