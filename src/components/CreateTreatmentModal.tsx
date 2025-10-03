import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { CalendarIcon, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useCreateTreatment } from '@/hooks/api/useTreatments';
import { useToast } from '@/hooks/use-toast';

interface CreateTreatmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  patientId: string;
  patientName: string;
}

const CreateTreatmentModal: React.FC<CreateTreatmentModalProps> = ({
  isOpen,
  onClose,
  patientId,
  patientName,
}) => {
  const { t } = useTranslation();
  const { toast } = useToast();
  const createTreatmentMutation = useCreateTreatment();

  const [formData, setFormData] = useState({
    treatment_type: '',
    medication_name: '',
    dosage: '',
    frequency: '',
    duration: '',
    start_date: new Date(),
    end_date: null as Date | null,
    status: 'ACTIVE',
    notes: '',
  });

  const treatmentTypes = [
    'Chimiothérapie',
    'Radiothérapie',
    'Immunothérapie',
    'Traitement symptomatique',
    'Chirurgie',
    'Thérapie ciblée',
    'Hormonothérapie',
    'Soins palliatifs',
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.treatment_type || !formData.start_date) {
      toast({
        title: "Erreur",
        description: "Veuillez remplir tous les champs obligatoires",
        variant: "destructive",
      });
      return;
    }

    try {
      await createTreatmentMutation.mutateAsync({
        patient_id: patientId,
        treatment_type: formData.treatment_type,
        medication_name: formData.medication_name || null,
        dosage: formData.dosage || null,
        frequency: formData.frequency || null,
        duration: formData.duration || null,
        start_date: formData.start_date.toISOString().split('T')[0],
        end_date: formData.end_date ? formData.end_date.toISOString().split('T')[0] : null,
        status: formData.status,
        notes: formData.notes || null,
      });

      toast({
        title: "Traitement créé",
        description: "Le traitement a été ajouté avec succès",
      });

      onClose();
      
      // Reset form
      setFormData({
        treatment_type: '',
        medication_name: '',
        dosage: '',
        frequency: '',
        duration: '',
        start_date: new Date(),
        end_date: null,
        status: 'ACTIVE',
        notes: '',
      });
    } catch (error) {
      console.error('Erreur création traitement:', error);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Nouveau Traitement</DialogTitle>
          <DialogDescription>
            Ajouter un nouveau traitement pour {patientName}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Type de traitement */}
            <div className="space-y-2">
              <Label htmlFor="treatment_type">Type de traitement *</Label>
              <Select
                value={formData.treatment_type}
                onValueChange={(value) => handleInputChange('treatment_type', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner un type" />
                </SelectTrigger>
                <SelectContent>
                  {treatmentTypes.map((type) => (
                    <SelectItem key={type} value={type}>
                      {type}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Médicament */}
            <div className="space-y-2">
              <Label htmlFor="medication_name">Médicament</Label>
              <Input
                id="medication_name"
                value={formData.medication_name}
                onChange={(e) => handleInputChange('medication_name', e.target.value)}
                placeholder="Nom du médicament"
              />
            </div>

            {/* Dosage */}
            <div className="space-y-2">
              <Label htmlFor="dosage">Dosage</Label>
              <Input
                id="dosage"
                value={formData.dosage}
                onChange={(e) => handleInputChange('dosage', e.target.value)}
                placeholder="ex: 150 mg/m²"
              />
            </div>

            {/* Fréquence */}
            <div className="space-y-2">
              <Label htmlFor="frequency">Fréquence</Label>
              <Input
                id="frequency"
                value={formData.frequency}
                onChange={(e) => handleInputChange('frequency', e.target.value)}
                placeholder="ex: 1 fois par jour"
              />
            </div>

            {/* Durée */}
            <div className="space-y-2">
              <Label htmlFor="duration">Durée</Label>
              <Input
                id="duration"
                value={formData.duration}
                onChange={(e) => handleInputChange('duration', e.target.value)}
                placeholder="ex: 6 cycles de 28 jours"
              />
            </div>

            {/* Statut */}
            <div className="space-y-2">
              <Label htmlFor="status">Statut</Label>
              <Select
                value={formData.status}
                onValueChange={(value) => handleInputChange('status', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ACTIVE">Actif</SelectItem>
                  <SelectItem value="SCHEDULED">Programmé</SelectItem>
                  <SelectItem value="SUSPENDED">Suspendu</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Date de début */}
            <div className="space-y-2">
              <Label>Date de début *</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      "w-full justify-start text-left font-normal",
                      !formData.start_date && "text-muted-foreground"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {formData.start_date ? format(formData.start_date, "PPP") : "Sélectionner une date"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={formData.start_date}
                    onSelect={(date) => handleInputChange('start_date', date || new Date())}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>

            {/* Date de fin */}
            <div className="space-y-2">
              <Label>Date de fin (optionnelle)</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      "w-full justify-start text-left font-normal",
                      !formData.end_date && "text-muted-foreground"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {formData.end_date ? format(formData.end_date, "PPP") : "Sélectionner une date"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={formData.end_date}
                    onSelect={(date) => handleInputChange('end_date', date)}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              placeholder="Notes sur le traitement..."
              rows={3}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Annuler
            </Button>
            <Button type="submit" disabled={createTreatmentMutation.isPending}>
              {createTreatmentMutation.isPending && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Créer le traitement
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default CreateTreatmentModal;
