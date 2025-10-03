import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';
import { 
  Users, 
  Plus, 
  Search, 
  Filter,
  MoreHorizontal,
  Edit,
  Eye,
  Calendar,
  FileText,
  Phone,
  Mail,
  User,
  Heart
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
import { usePatients } from '@/hooks/usePatients';
import { useAuth } from '@/contexts/AuthContext';
import { usePermissions } from '@/utils/permissions';

const PatientManagement: React.FC = () => {
  const { t } = useTranslation();
  const { userData } = useAuth();
  const permissions = usePermissions(userData);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGender, setSelectedGender] = useState<'ALL' | 'MALE' | 'FEMALE'>('ALL');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  // Hook pour récupérer les patients (filtrés automatiquement par le backend selon assigned_doctor_id)
  const { data: patientsData, isLoading, error } = usePatients(currentPage, pageSize);

  // Filtrage côté client
  const filteredPatients = patientsData?.items?.filter((patient: any) => {
    const matchesSearch = 
      patient.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.email?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesGender = selectedGender === 'ALL' || patient.gender === selectedGender;
    
    return matchesSearch && matchesGender;
  }) || [];

  // Calculer l'âge
  const calculateAge = (dateOfBirth: string) => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    return age;
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Gestion des Patients
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-medical mx-auto mb-4"></div>
              <p className="text-muted-foreground">Chargement des patients...</p>
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
            <Users className="h-5 w-5" />
            Gestion des Patients
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="h-8 w-8 text-destructive mx-auto mb-4">⚠️</div>
              <p className="text-destructive">Erreur lors du chargement des patients</p>
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
              <Users className="h-5 w-5" />
              Gestion des Patients
            </CardTitle>
            <CardDescription>
              Patients assignés à votre médecin - Gestion administrative
            </CardDescription>
          </div>
          {permissions.canCreatePatients && (
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Nouveau Patient
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {/* Statistiques rapides */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{patientsData?.total || 0}</div>
            <div className="text-sm text-blue-600">Total Patients</div>
          </div>
          <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {filteredPatients.filter((p: any) => p.gender === 'MALE').length}
            </div>
            <div className="text-sm text-green-600">Hommes</div>
          </div>
          <div className="bg-pink-50 dark:bg-pink-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-pink-600">
              {filteredPatients.filter((p: any) => p.gender === 'FEMALE').length}
            </div>
            <div className="text-sm text-pink-600">Femmes</div>
          </div>
          <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {userData?.assigned_doctor_id ? 'Assignés' : 'Non assignés'}
            </div>
            <div className="text-sm text-purple-600">Statut</div>
          </div>
        </div>

        {/* Filtres et recherche */}
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Rechercher un patient..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline">
                <Filter className="mr-2 h-4 w-4" />
                {selectedGender === 'ALL' ? 'Tous' : selectedGender === 'MALE' ? 'Hommes' : 'Femmes'}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => setSelectedGender('ALL')}>
                Tous les patients
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => setSelectedGender('MALE')}>
                Hommes
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setSelectedGender('FEMALE')}>
                Femmes
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Table des patients */}
        <div className="border rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Patient</TableHead>
                <TableHead>Âge/Genre</TableHead>
                <TableHead>Contact</TableHead>
                <TableHead>Dernière visite</TableHead>
                <TableHead>Statut</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredPatients.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8">
                    <div className="text-muted-foreground">
                      {searchTerm || selectedGender !== 'ALL' 
                        ? 'Aucun patient trouvé avec ces critères'
                        : 'Aucun patient assigné'
                      }
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                filteredPatients.map((patient: any) => (
                  <TableRow key={patient.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
                          patient.gender === 'MALE' 
                            ? 'bg-blue-100 dark:bg-blue-800' 
                            : 'bg-pink-100 dark:bg-pink-800'
                        }`}>
                          <User className={`h-4 w-4 ${
                            patient.gender === 'MALE' ? 'text-blue-600' : 'text-pink-600'
                          }`} />
                        </div>
                        <div>
                          <div className="font-medium">
                            {patient.first_name} {patient.last_name}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            ID: {patient.id.slice(0, 8)}...
                          </div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        <div>{calculateAge(patient.date_of_birth)} ans</div>
                        <Badge variant={patient.gender === 'MALE' ? 'default' : 'secondary'} className="text-xs">
                          {patient.gender === 'MALE' ? 'H' : 'F'}
                        </Badge>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        {patient.email && (
                          <div className="text-sm flex items-center gap-1">
                            <Mail className="h-3 w-3" />
                            {patient.email}
                          </div>
                        )}
                        {patient.phone && (
                          <div className="text-sm flex items-center gap-1">
                            <Phone className="h-3 w-3" />
                            {patient.phone}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {patient.last_visit ? format(new Date(patient.last_visit), 'dd/MM/yyyy') : 'Aucune'}
                    </TableCell>
                    <TableCell>
                      <Badge variant="default" className="bg-green-100 text-green-800">
                        <Heart className="h-3 w-3 mr-1" />
                        Actif
                      </Badge>
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
                            <Eye className="mr-2 h-4 w-4" />
                            Voir détails
                          </DropdownMenuItem>
                          {permissions.canEditPatients && (
                            <DropdownMenuItem>
                              <Edit className="mr-2 h-4 w-4" />
                              Modifier
                            </DropdownMenuItem>
                          )}
                          <DropdownMenuSeparator />
                          <DropdownMenuItem>
                            <Calendar className="mr-2 h-4 w-4" />
                            Planifier RDV
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <FileText className="mr-2 h-4 w-4" />
                            Voir rapports
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>

        {/* Pagination */}
        {patientsData && patientsData.pages > 1 && (
          <div className="flex items-center justify-between mt-6">
            <div className="text-sm text-muted-foreground">
              Page {currentPage} sur {patientsData.pages} ({patientsData.total} patients)
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
              >
                Précédent
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(prev => Math.min(patientsData.pages, prev + 1))}
                disabled={currentPage === patientsData.pages}
              >
                Suivant
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PatientManagement;
