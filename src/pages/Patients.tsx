import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import {
  PlusCircle,
  Search,
  FileText,
  MoreHorizontal,
  Pencil,
  Trash2,
  Eye,
  Filter,
  Calendar as CalendarIcon,
  LayoutGrid,
  LayoutList,
  Download,
  FileSpreadsheet,
  File, // Using File instead of FilePdf
  ChevronUp,
  ChevronDown,
  X,
  AlertCircle
} from 'lucide-react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
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
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { useToast } from '@/hooks/use-toast';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination';
import { format } from 'date-fns';
import { Patient } from '@/services/api';
import { usePatients } from '@/hooks/usePatients';
import { useSegmentationWorkflow } from '@/hooks/useSegmentation';
import { useAuth } from '@/contexts/AuthContext';

// Import export utilities
import { exportToPDF, exportToExcel } from '@/utils/exportUtils';

// Calculate age from date of birth
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

// Adapter pour convertir les données API vers le format attendu
const adaptPatientData = (apiPatient: Patient, t: any) => {
  // Récupérer le nom du médecin assigné
  let doctorName = t('patients.noAssignedDoctor');
  if (apiPatient.assigned_doctor) {
    const doctor = apiPatient.assigned_doctor;
    if (doctor.user) {
      doctorName = `Dr. ${doctor.user.first_name} ${doctor.user.last_name}`;
    } else {
      doctorName = 'Dr. Assigné';
    }
  }

  return {
    id: apiPatient.id,
    firstName: apiPatient.first_name,
    lastName: apiPatient.last_name,
    dateOfBirth: apiPatient.date_of_birth,
    gender: apiPatient.gender === 'MALE' ? 'Male' : 'Female',
    contactNumber: apiPatient.phone || 'N/A',
    email: apiPatient.email || 'N/A',
    doctor: doctorName,
    lastScan: new Date().toISOString(), // À récupérer depuis l'API
    lastVisit: new Date().toISOString(), // À récupérer depuis l'API
  };
};

// Patient Card Component
interface PatientCardProps {
  patient: Patient;
  onDelete: (id: string) => void;
  setPatientToDelete: (id: string | null) => void;
}

const PatientCard: React.FC<PatientCardProps> = ({ patient, onDelete, setPatientToDelete }) => {
  const { t } = useTranslation();
  const { currentUser } = useAuth();
  const age = calculateAge(patient.dateOfBirth);

  // Déterminer si le médecin assigné doit être affiché
  const showDoctorInfo = currentUser?.role === 'ADMIN';

  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex justify-between">
          <span>{patient.firstName} {patient.lastName}</span>
          <span className="text-sm text-muted-foreground">ID: {patient.id}</span>
        </CardTitle>
        <CardDescription>
          {age} {t('common.yearsOld')} • {patient.gender}
        </CardDescription>
      </CardHeader>
      <CardContent className="pb-2">
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">{t('patients.contactNumber')}:</span>
            <span>{patient.contactNumber}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">{t('patients.dateOfBirth')}:</span>
            <span>{new Date(patient.dateOfBirth).toLocaleDateString()}</span>
          </div>
          {showDoctorInfo && (
            <div className="flex justify-between">
              <span className="text-muted-foreground">{t('patients.assignedDoctor')}:</span>
              <span>{patient.doctor}</span>
            </div>
          )}
          <div className="flex justify-between">
            <span className="text-muted-foreground">{t('patients.lastScan')}:</span>
            <span>{new Date(patient.lastScan).toLocaleDateString()}</span>
          </div>
        </div>
      </CardContent>
      <CardFooter className="pt-2 flex justify-between">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm">
              {t('common.actions')}
              <ChevronDown className="ml-2 h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem asChild>
              <Link to={`/patients/${patient.id}`} className="flex items-center">
                <Eye className="mr-2 h-4 w-4" />
                <span>{t('common.view')}</span>
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <Link to={`/patients/${patient.id}/edit`} className="flex items-center">
                <Pencil className="mr-2 h-4 w-4" />
                <span>{t('common.edit')}</span>
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <Link to={`/patients/${patient.id}/scans`} className="flex items-center">
                <FileText className="mr-2 h-4 w-4" />
                <span>{t('navigation.scans')}</span>
              </Link>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <DropdownMenuItem
                  className="text-red-500 focus:text-red-500"
                  onSelect={(e) => {
                    e.preventDefault();
                    setPatientToDelete(patient.id);
                  }}
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  <span>{t('common.delete')}</span>
                </DropdownMenuItem>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>{t('patients.deletePatient')}</AlertDialogTitle>
                  <AlertDialogDescription>
                    {t('patients.deleteConfirmation')}
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>{t('common.cancel')}</AlertDialogCancel>
                  <AlertDialogAction
                    className="bg-red-500 hover:bg-red-600"
                    onClick={() => onDelete(patient.id)}
                  >
                    {t('common.delete')}
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </DropdownMenuContent>
        </DropdownMenu>
      </CardFooter>
    </Card>
  );
};

const Patients: React.FC = () => {
  const { t } = useTranslation();
  const { toast } = useToast();

  // Récupérer l'utilisateur connecté pour déterminer les permissions d'affichage
  const { currentUser } = useAuth();

  // State for search and filters
  const [searchQuery, setSearchQuery] = useState('');
  const [patientToDelete, setPatientToDelete] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'table' | 'card'>('table');
  const [showFilters, setShowFilters] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);

  // Récupération des données depuis l'API
  const { data: patientsData, isLoading, error } = usePatients(currentPage, itemsPerPage);

  // Déterminer si la colonne "Médecin assigné" doit être affichée
  const showDoctorColumn = currentUser?.role === 'ADMIN';

  // Adapter les données pour le composant existant
  const patients = patientsData?.items?.map(patient => adaptPatientData(patient, t)) || [];

  // Filter states
  const [ageRange, setAgeRange] = useState<[number | null, number | null]>([null, null]);
  const [genderFilter, setGenderFilter] = useState<string | null>(null);
  const [doctorFilter, setDoctorFilter] = useState<string | null>(null);
  const [admissionDateRange, setAdmissionDateRange] = useState<[Date | null, Date | null]>([null, null]);
  const [tumorTypeFilter, setTumorTypeFilter] = useState<string | null>(null);

  // Sorting state
  const [sortField, setSortField] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  // Get unique doctors for filter dropdown
  const uniqueDoctors = Array.from(new Set(patients.map(patient => patient.doctor)));

  // Get unique tumor types (simplified for now)
  const uniqueTumorTypes = ['Glioblastoma', 'Meningioma', 'Astrocytoma', 'Pituitary Adenoma'];

  // Apply all filters
  const applyFilters = (patient: Patient) => {
    // Text search filter
    const matchesSearch =
      patient.firstName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      patient.lastName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      patient.contactNumber.includes(searchQuery) ||
      patient.email.toLowerCase().includes(searchQuery.toLowerCase());

    if (!matchesSearch) return false;

    // Age filter
    const age = calculateAge(patient.dateOfBirth);
    if (ageRange[0] !== null && age < ageRange[0]) return false;
    if (ageRange[1] !== null && age > ageRange[1]) return false;

    // Gender filter
    if (genderFilter && patient.gender !== genderFilter) return false;

    // Doctor filter
    if (doctorFilter && patient.doctor !== doctorFilter) return false;

    // Admission date filter (using lastVisit as proxy for admission date)
    if (admissionDateRange[0] && new Date(patient.lastVisit) < admissionDateRange[0]) return false;
    if (admissionDateRange[1] && new Date(patient.lastVisit) > admissionDateRange[1]) return false;

    // Tumor type filter (simplified for now)
    // TODO: Implement with real segmentation data from API

    return true;
  };

  // Apply sorting
  const applySorting = (a: Patient, b: Patient) => {
    if (!sortField) return 0;

    let valueA, valueB;

    switch (sortField) {
      case 'id':
        valueA = a.id;
        valueB = b.id;
        break;
      case 'firstName':
        valueA = a.firstName;
        valueB = b.firstName;
        break;
      case 'lastName':
        valueA = a.lastName;
        valueB = b.lastName;
        break;
      case 'dateOfBirth':
        valueA = new Date(a.dateOfBirth).getTime();
        valueB = new Date(b.dateOfBirth).getTime();
        break;
      case 'age':
        valueA = calculateAge(a.dateOfBirth);
        valueB = calculateAge(b.dateOfBirth);
        break;
      case 'gender':
        valueA = a.gender;
        valueB = b.gender;
        break;
      case 'doctor':
        valueA = a.doctor;
        valueB = b.doctor;
        break;
      case 'lastScan':
        valueA = new Date(a.lastScan).getTime();
        valueB = new Date(b.lastScan).getTime();
        break;
      default:
        return 0;
    }

    if (valueA < valueB) return sortDirection === 'asc' ? -1 : 1;
    if (valueA > valueB) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  };

  // Get filtered and sorted patients
  const filteredPatients = patients.filter(applyFilters).sort(applySorting);

  // Apply pagination
  const paginatedPatients = filteredPatients.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const totalPages = Math.ceil(filteredPatients.length / itemsPerPage);

  // Handle sorting
  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Reset filters
  const resetFilters = () => {
    setSearchQuery('');
    setAgeRange([null, null]);
    setGenderFilter(null);
    setDoctorFilter(null);
    setAdmissionDateRange([null, null]);
    setTumorTypeFilter(null);
    setSortField(null);
    setSortDirection('asc');
    setCurrentPage(1);
  };

  // Handle delete patient
  const handleDeletePatient = (id: string) => {
    // TODO: Implement delete with API
    toast({
      title: "Suppression",
      description: "Fonctionnalité de suppression à implémenter avec l'API",
      variant: "destructive",
    });
    setPatientToDelete(null);
  };

  // Handle export
  const handleExport = (format: 'pdf' | 'excel') => {
    if (format === 'pdf') {
      exportToPDF(filteredPatients);
    } else {
      exportToExcel(filteredPatients);
    }
  };

  // Gestion des erreurs
  if (error) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
                <h3 className="text-lg font-semibold mb-2">Erreur de chargement</h3>
                <p className="text-muted-foreground mb-4">
                  Impossible de charger les patients: {error.message}
                </p>
                <Button onClick={() => window.location.reload()}>
                  Réessayer
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              {t('patients.patients')} {isLoading ? `(${t('common.loading')})` : `(${patientsData?.total || 0})`}
            </h1>
            <p className="text-muted-foreground">
              {t('patients.patientManagementDescription')}
            </p>
          </div>
          <div className="flex gap-2 mt-4 md:mt-0">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline">
                  <Download className="mr-2 h-4 w-4" />
                  {t('common.export')}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => handleExport('pdf')}>
                  <File className="mr-2 h-4 w-4" />
                  <span>{t('common.exportPDF')}</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleExport('excel')}>
                  <FileSpreadsheet className="mr-2 h-4 w-4" />
                  <span>{t('common.exportExcel')}</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            <Button asChild>
              <Link to="/patients/new">
                <PlusCircle className="mr-2 h-4 w-4" />
                {t('patients.addPatient')}
              </Link>
            </Button>
          </div>
        </div>

        {/* Search and filters */}
        <div className="mb-6 space-y-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder={t('common.search')}
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setShowFilters(!showFilters)}
                className={showFilters ? "bg-muted" : ""}
              >
                <Filter className="mr-2 h-4 w-4" />
                {t('common.filters')}
              </Button>
              <Button
                variant="outline"
                onClick={() => setViewMode(viewMode === 'table' ? 'card' : 'table')}
              >
                {viewMode === 'table' ? (
                  <LayoutGrid className="mr-2 h-4 w-4" />
                ) : (
                  <LayoutList className="mr-2 h-4 w-4" />
                )}
                {viewMode === 'table' ? t('common.cardView') : t('common.tableView')}
              </Button>
            </div>
          </div>

          {/* Advanced filters */}
          {showFilters && (
            <div className="p-4 border rounded-md bg-muted/30 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium">{t('common.advancedFilters')}</h3>
                <div className="flex gap-2">
                  <Button variant="ghost" size="sm" onClick={resetFilters}>
                    <X className="mr-2 h-4 w-4" />
                    {t('common.resetFilters')}
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Age range filter */}
                <div className="space-y-2">
                  <label className="text-sm font-medium">{t('patients.ageRange')}</label>
                  <div className="flex gap-2">
                    <Input
                      type="number"
                      placeholder={t('common.min')}
                      value={ageRange[0] !== null ? ageRange[0] : ''}
                      onChange={(e) => setAgeRange([e.target.value ? parseInt(e.target.value) : null, ageRange[1]])}
                      className="w-full"
                    />
                    <Input
                      type="number"
                      placeholder={t('common.max')}
                      value={ageRange[1] !== null ? ageRange[1] : ''}
                      onChange={(e) => setAgeRange([ageRange[0], e.target.value ? parseInt(e.target.value) : null])}
                      className="w-full"
                    />
                  </div>
                </div>

                {/* Gender filter */}
                <div className="space-y-2">
                  <label className="text-sm font-medium">{t('patients.gender')}</label>
                  <Select
                    value={genderFilter || 'all'}
                    onValueChange={(value) => setGenderFilter(value === 'all' ? null : value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={t('common.selectGender')} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">{t('common.all')}</SelectItem>
                      <SelectItem value="Male">{t('common.male')}</SelectItem>
                      <SelectItem value="Female">{t('common.female')}</SelectItem>
                      <SelectItem value="Other">{t('common.other')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Doctor filter */}
                <div className="space-y-2">
                  <label className="text-sm font-medium">{t('patients.assignedDoctor')}</label>
                  <Select
                    value={doctorFilter || 'all'}
                    onValueChange={(value) => setDoctorFilter(value === 'all' ? null : value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={t('common.selectDoctor')} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">{t('common.all')}</SelectItem>
                      {uniqueDoctors.map((doctor) => (
                        <SelectItem key={doctor} value={doctor}>
                          {doctor}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Tumor type filter */}
                <div className="space-y-2">
                  <label className="text-sm font-medium">{t('scans.tumorType')}</label>
                  <Select
                    value={tumorTypeFilter || 'all'}
                    onValueChange={(value) => setTumorTypeFilter(value === 'all' ? null : value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={t('common.selectTumorType')} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">{t('common.all')}</SelectItem>
                      {uniqueTumorTypes.map((type) => (
                        <SelectItem key={type} value={type}>
                          {type}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Admission date filter */}
                <div className="space-y-2">
                  <label className="text-sm font-medium">{t('patients.admissionDate')}</label>
                  <div className="flex gap-2">
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          className="w-full justify-start text-left font-normal"
                        >
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {admissionDateRange[0] ? (
                            format(admissionDateRange[0], 'PPP')
                          ) : (
                            <span>{t('common.startDate')}</span>
                          )}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0">
                        <Calendar
                          mode="single"
                          selected={admissionDateRange[0] || undefined}
                          onSelect={(date) => setAdmissionDateRange([date, admissionDateRange[1]])}
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          className="w-full justify-start text-left font-normal"
                        >
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {admissionDateRange[1] ? (
                            format(admissionDateRange[1], 'PPP')
                          ) : (
                            <span>{t('common.endDate')}</span>
                          )}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0">
                        <Calendar
                          mode="single"
                          selected={admissionDateRange[1] || undefined}
                          onSelect={(date) => setAdmissionDateRange([admissionDateRange[0], date])}
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Results count */}
        <div className="mb-4 text-sm text-muted-foreground">
          {t('common.showing')} <strong>{paginatedPatients.length}</strong> {t('common.of')}{' '}
          <strong>{filteredPatients.length}</strong> {t('patients.patients')}
        </div>

        {/* Table view */}
        {viewMode === 'table' ? (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead
                    className="cursor-pointer"
                    onClick={() => handleSort('id')}
                  >
                    <div className="flex items-center">
                      {t('patients.patientId')}
                      {sortField === 'id' && (
                        sortDirection === 'asc' ?
                          <ChevronUp className="ml-1 h-4 w-4" /> :
                          <ChevronDown className="ml-1 h-4 w-4" />
                      )}
                    </div>
                  </TableHead>
                  <TableHead
                    className="cursor-pointer"
                    onClick={() => handleSort('firstName')}
                  >
                    <div className="flex items-center">
                      {t('patients.firstName')}
                      {sortField === 'firstName' && (
                        sortDirection === 'asc' ?
                          <ChevronUp className="ml-1 h-4 w-4" /> :
                          <ChevronDown className="ml-1 h-4 w-4" />
                      )}
                    </div>
                  </TableHead>
                  <TableHead
                    className="cursor-pointer"
                    onClick={() => handleSort('lastName')}
                  >
                    <div className="flex items-center">
                      {t('patients.lastName')}
                      {sortField === 'lastName' && (
                        sortDirection === 'asc' ?
                          <ChevronUp className="ml-1 h-4 w-4" /> :
                          <ChevronDown className="ml-1 h-4 w-4" />
                      )}
                    </div>
                  </TableHead>
                  <TableHead
                    className="hidden md:table-cell cursor-pointer"
                    onClick={() => handleSort('dateOfBirth')}
                  >
                    <div className="flex items-center">
                      {t('patients.dateOfBirth')}
                      {sortField === 'dateOfBirth' && (
                        sortDirection === 'asc' ?
                          <ChevronUp className="ml-1 h-4 w-4" /> :
                          <ChevronDown className="ml-1 h-4 w-4" />
                      )}
                    </div>
                  </TableHead>
                  <TableHead
                    className="hidden md:table-cell cursor-pointer"
                    onClick={() => handleSort('gender')}
                  >
                    <div className="flex items-center">
                      {t('patients.gender')}
                      {sortField === 'gender' && (
                        sortDirection === 'asc' ?
                          <ChevronUp className="ml-1 h-4 w-4" /> :
                          <ChevronDown className="ml-1 h-4 w-4" />
                      )}
                    </div>
                  </TableHead>
                  <TableHead className="hidden lg:table-cell">{t('patients.contactNumber')}</TableHead>
                  {showDoctorColumn && (
                    <TableHead
                      className="hidden lg:table-cell cursor-pointer"
                      onClick={() => handleSort('doctor')}
                    >
                      <div className="flex items-center">
                        {t('patients.assignedDoctor')}
                        {sortField === 'doctor' && (
                          sortDirection === 'asc' ?
                            <ChevronUp className="ml-1 h-4 w-4" /> :
                            <ChevronDown className="ml-1 h-4 w-4" />
                        )}
                      </div>
                    </TableHead>
                  )}
                  <TableHead className="text-right">{t('common.actions')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {paginatedPatients.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={showDoctorColumn ? 8 : 7} className="text-center py-6 text-muted-foreground">
                      {t('patients.noPatients')}
                    </TableCell>
                  </TableRow>
                ) : (
                  paginatedPatients.map((patient) => (
                    <TableRow key={patient.id}>
                      <TableCell>{patient.id}</TableCell>
                      <TableCell>{patient.firstName}</TableCell>
                      <TableCell>{patient.lastName}</TableCell>
                      <TableCell className="hidden md:table-cell">
                        {new Date(patient.dateOfBirth).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="hidden md:table-cell">{patient.gender}</TableCell>
                      <TableCell className="hidden lg:table-cell">{patient.contactNumber}</TableCell>
                      {showDoctorColumn && (
                        <TableCell className="hidden lg:table-cell">{patient.doctor}</TableCell>
                      )}
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreHorizontal className="h-4 w-4" />
                              <span className="sr-only">Open menu</span>
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>{t('common.actions')}</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem asChild>
                              <Link to={`/patients/${patient.id}`} className="flex items-center">
                                <Eye className="mr-2 h-4 w-4" />
                                <span>{t('common.view')}</span>
                              </Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem asChild>
                              <Link to={`/patients/${patient.id}/edit`} className="flex items-center">
                                <Pencil className="mr-2 h-4 w-4" />
                                <span>{t('common.edit')}</span>
                              </Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem asChild>
                              <Link to={`/patients/${patient.id}/scans`} className="flex items-center">
                                <FileText className="mr-2 h-4 w-4" />
                                <span>{t('navigation.scans')}</span>
                              </Link>
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <AlertDialog open={patientToDelete === patient.id} onOpenChange={(open) => !open && setPatientToDelete(null)}>
                              <AlertDialogTrigger asChild>
                                <DropdownMenuItem
                                  className="text-red-500 focus:text-red-500"
                                  onSelect={(e) => {
                                    e.preventDefault();
                                    setPatientToDelete(patient.id);
                                  }}
                                >
                                  <Trash2 className="mr-2 h-4 w-4" />
                                  <span>{t('common.delete')}</span>
                                </DropdownMenuItem>
                              </AlertDialogTrigger>
                              <AlertDialogContent>
                                <AlertDialogHeader>
                                  <AlertDialogTitle>{t('patients.deletePatient')}</AlertDialogTitle>
                                  <AlertDialogDescription>
                                    {t('patients.deleteConfirmation')}
                                  </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                  <AlertDialogCancel>{t('common.cancel')}</AlertDialogCancel>
                                  <AlertDialogAction
                                    className="bg-red-500 hover:bg-red-600"
                                    onClick={() => handleDeletePatient(patient.id)}
                                  >
                                    {t('common.delete')}
                                  </AlertDialogAction>
                                </AlertDialogFooter>
                              </AlertDialogContent>
                            </AlertDialog>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        ) : (
          // Card view
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {paginatedPatients.length === 0 ? (
              <div className="col-span-full text-center py-6 text-muted-foreground">
                {t('patients.noPatients')}
              </div>
            ) : (
              paginatedPatients.map((patient) => (
                <PatientCard
                  key={patient.id}
                  patient={patient}
                  onDelete={handleDeletePatient}
                  setPatientToDelete={setPatientToDelete}
                />
              ))
            )}
          </div>
        )}

        {/* Pagination */}
        {filteredPatients.length > 0 && (
          <div className="mt-6">
            <Pagination>
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    className={currentPage === 1 ? "pointer-events-none opacity-50" : ""}
                  />
                </PaginationItem>

                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  // Show first page, last page, current page, and pages around current
                  let pageToShow;
                  if (totalPages <= 5) {
                    // If 5 or fewer pages, show all
                    pageToShow = i + 1;
                  } else if (currentPage <= 3) {
                    // Near start
                    if (i < 4) {
                      pageToShow = i + 1;
                    } else {
                      pageToShow = totalPages;
                    }
                  } else if (currentPage >= totalPages - 2) {
                    // Near end
                    if (i === 0) {
                      pageToShow = 1;
                    } else {
                      pageToShow = totalPages - (4 - i);
                    }
                  } else {
                    // Middle
                    if (i === 0) {
                      pageToShow = 1;
                    } else if (i === 4) {
                      pageToShow = totalPages;
                    } else {
                      pageToShow = currentPage + (i - 2);
                    }
                  }

                  // Add ellipsis if needed
                  if ((i === 1 && pageToShow > 2) || (i === 3 && pageToShow < totalPages - 1)) {
                    return (
                      <PaginationItem key={`ellipsis-${i}`}>
                        <PaginationEllipsis />
                      </PaginationItem>
                    );
                  }

                  return (
                    <PaginationItem key={pageToShow}>
                      <PaginationLink
                        isActive={currentPage === pageToShow}
                        onClick={() => setCurrentPage(pageToShow)}
                      >
                        {pageToShow}
                      </PaginationLink>
                    </PaginationItem>
                  );
                })}

                <PaginationItem>
                  <PaginationNext
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    className={currentPage === totalPages ? "pointer-events-none opacity-50" : ""}
                  />
                </PaginationItem>
              </PaginationContent>
            </Pagination>

            <div className="mt-2 text-center text-sm text-muted-foreground">
              {t('common.page')} {currentPage} {t('common.of')} {totalPages}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default Patients;
