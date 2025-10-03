import React, { useState, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Upload, X, FileImage, AlertCircle, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';
import { useImageUpload } from '@/hooks/api/useImageUpload';

// Types pour les modalités d'images
type ImageModality = 'T1' | 'T1CE' | 'T2' | 'FLAIR';

interface ModalityFile {
  modality: ImageModality;
  file: File | null;
  preview?: string;
}

// Schéma de validation
const uploadSchema = z.object({
  patient_id: z.string().min(1, 'ID patient requis'),
  acquisition_date: z.string().optional(),
  notes: z.string().optional(),
});

type UploadFormData = z.infer<typeof uploadSchema>;

interface ImageUploadFormProps {
  patientId: string;
  onUploadComplete: (imageIds: string[]) => void;
  onCancel: () => void;
}

const ImageUploadForm: React.FC<ImageUploadFormProps> = ({
  patientId,
  onUploadComplete,
  onCancel,
}) => {
  const { toast } = useToast();
  const uploadMutation = useImageUpload();
  const [modalityFiles, setModalityFiles] = useState<ModalityFile[]>([
    { modality: 'T1', file: null },
    { modality: 'T1CE', file: null },
    { modality: 'T2', file: null },
    { modality: 'FLAIR', file: null },
  ]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRefs = useRef<{ [key in ImageModality]: HTMLInputElement | null }>({
    T1: null,
    T1CE: null,
    T2: null,
    FLAIR: null,
  });

  const form = useForm<UploadFormData>({
    resolver: zodResolver(uploadSchema),
    defaultValues: {
      patient_id: patientId,
      acquisition_date: new Date().toISOString().split('T')[0],
      notes: '',
    },
  });

  // Validation des fichiers
  const validateFile = (file: File): boolean => {
    const validExtensions = ['.nii', '.nii.gz', '.dcm', '.dicom'];
    const maxSize = 500 * 1024 * 1024; // 500MB

    if (file.size > maxSize) {
      toast({
        title: "Fichier trop volumineux",
        description: "La taille maximale autorisée est de 500MB",
        variant: "destructive",
      });
      return false;
    }

    const hasValidExtension = validExtensions.some(ext =>
      file.name.toLowerCase().endsWith(ext)
    );

    if (!hasValidExtension) {
      toast({
        title: "Format non supporté",
        description: "Formats acceptés: .nii, .nii.gz, .dcm, .dicom",
        variant: "destructive",
      });
      return false;
    }

    return true;
  };

  // Gestion de la sélection de fichier
  const handleFileSelect = (modality: ImageModality, file: File) => {
    if (!validateFile(file)) return;

    setModalityFiles(prev => prev.map(item =>
      item.modality === modality
        ? { ...item, file, preview: URL.createObjectURL(file) }
        : item
    ));
  };

  // Suppression d'un fichier
  const removeFile = (modality: ImageModality) => {
    setModalityFiles(prev => prev.map(item =>
      item.modality === modality
        ? { ...item, file: null, preview: undefined }
        : item
    ));

    if (fileInputRefs.current[modality]) {
      fileInputRefs.current[modality]!.value = '';
    }
  };

  // Soumission du formulaire
  const handleSubmit = async (data: UploadFormData) => {
    const filesToUpload = modalityFiles.filter(item => item.file);

    if (filesToUpload.length === 0) {
      toast({
        title: "Aucun fichier sélectionné",
        description: "Veuillez sélectionner au moins une modalité d'image",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Créer FormData pour l'upload
      const formData = new FormData();
      formData.append('patient_id', data.patient_id);

      if (data.acquisition_date) {
        formData.append('acquisition_date', data.acquisition_date);
      }

      if (data.notes) {
        formData.append('notes', data.notes);
      }

      // Ajouter les fichiers avec leurs modalités
      filesToUpload.forEach((item, index) => {
        if (item.file) {
          formData.append(`${item.modality.toLowerCase()}_file`, item.file);
        }
      });

      // Simulation du progrès (à remplacer par vraie API)
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // Préparer les données pour l'API
      const uploadData = {
        patient_id: patientId,
        acquisition_date: data.acquisition_date,
        notes: data.notes,
        files: filesToUpload.map(item => ({
          modality: item.modality,
          file: item.file!
        }))
      };

      // Appel API réel
      const result = await uploadMutation.mutateAsync(uploadData);

      clearInterval(progressInterval);
      setUploadProgress(100);



      const uploadedCount = result?.uploaded_modalities?.length || 0;
      toast({
        title: "Upload réussi",
        description: `${uploadedCount} modalité(s) uploadée(s) avec succès`,
      });

      // Retourner les modalités uploadées (on peut utiliser les noms de fichiers comme IDs temporaires)
      const imageIds = result?.uploaded_modalities?.map(mod => mod.filename) || [];
      onUploadComplete(imageIds);

    } catch (error) {
      toast({
        title: "Erreur d'upload",
        description: error instanceof Error ? error.message : "Erreur inconnue",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const getModalityColor = (modality: ImageModality) => {
    const colors = {
      T1: 'bg-blue-100 text-blue-800 border-blue-200',
      T1CE: 'bg-green-100 text-green-800 border-green-200',
      T2: 'bg-purple-100 text-purple-800 border-purple-200',
      FLAIR: 'bg-orange-100 text-orange-800 border-orange-200',
    };
    return colors[modality];
  };

  const getModalityDescription = (modality: ImageModality) => {
    const descriptions = {
      T1: 'T1-weighted - Anatomie structurelle',
      T1CE: 'T1 avec contraste - Tumeurs rehaussées',
      T2: 'T2-weighted - Œdème et liquides',
      FLAIR: 'FLAIR - Suppression liquide céphalorachidien',
    };
    return descriptions[modality];
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5 text-medical" />
          Upload Images Médicales
        </CardTitle>
        <CardDescription>
          Uploadez les modalités d'images IRM pour le patient.
          Formats supportés: .nii, .nii.gz, .dcm, .dicom (max 500MB par fichier)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            {/* Informations générales */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="acquisition_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Date d'acquisition</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="notes"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Notes</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Notes sur l'acquisition..."
                        className="resize-none"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {/* Upload des modalités */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Modalités d'images</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {modalityFiles.map((item) => (
                  <ModalityUploadCard
                    key={item.modality}
                    modality={item.modality}
                    file={item.file}
                    preview={item.preview}
                    onFileSelect={(file) => handleFileSelect(item.modality, file)}
                    onRemove={() => removeFile(item.modality)}
                    getColor={getModalityColor}
                    getDescription={getModalityDescription}
                    fileInputRef={(ref) => fileInputRefs.current[item.modality] = ref}
                    disabled={isUploading}
                  />
                ))}
              </div>
            </div>

            {/* Progrès d'upload */}
            {isUploading && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Upload en cours...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <Progress value={uploadProgress} className="w-full" />
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-end space-x-4 pt-6">
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={isUploading}
              >
                Annuler
              </Button>
              <Button
                type="submit"
                disabled={isUploading || modalityFiles.every(item => !item.file)}
              >
                {isUploading ? 'Upload en cours...' : 'Uploader les images'}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
};

// Composant pour chaque modalité
interface ModalityUploadCardProps {
  modality: ImageModality;
  file: File | null;
  preview?: string;
  onFileSelect: (file: File) => void;
  onRemove: () => void;
  getColor: (modality: ImageModality) => string;
  getDescription: (modality: ImageModality) => string;
  fileInputRef: (ref: HTMLInputElement | null) => void;
  disabled: boolean;
}

const ModalityUploadCard: React.FC<ModalityUploadCardProps> = ({
  modality,
  file,
  preview,
  onFileSelect,
  onRemove,
  getColor,
  getDescription,
  fileInputRef,
  disabled,
}) => {
  const inputRef = React.useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      onFileSelect(selectedFile);
    }
  };

  const handleButtonClick = () => {
    inputRef.current?.click();
  };

  return (
    <Card className={`border-2 border-dashed transition-all ${
      file ? 'border-green-300 bg-green-50' : 'border-gray-300 hover:border-medical'
    }`}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <Badge className={getColor(modality)}>
            {modality}
          </Badge>
          {file && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={onRemove}
              disabled={disabled}
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>

        <p className="text-sm text-muted-foreground mb-3">
          {getDescription(modality)}
        </p>

        {!file ? (
          <div className="text-center">
            <input
              type="file"
              ref={inputRef}
              onChange={handleFileChange}
              accept=".nii,.nii.gz,.dcm,.dicom"
              className="hidden"
              disabled={disabled}
            />
            <Button
              type="button"
              variant="outline"
              onClick={handleButtonClick}
              disabled={disabled}
              className="w-full"
            >
              <Upload className="h-4 w-4 mr-2" />
              Sélectionner fichier
            </Button>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-sm">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <span className="truncate">{file.name}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ImageUploadForm;
