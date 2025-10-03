
import { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { Upload, Image, X, AlertCircle } from 'lucide-react';

interface UploadAreaProps {
  onFileSelect: (file: File) => void;
  isLoading: boolean;
}

const UploadArea = ({ onFileSelect, isLoading }: UploadAreaProps) => {
  const { t } = useTranslation();
  const [isDragging, setIsDragging] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const validateFile = (file: File): boolean => {
    // Check file type
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff'];
    if (!validTypes.includes(file.type)) {
      setError(t('scans.invalidFileType'));
      return false;
    }

    // Check file size (max 10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      setError(t('scans.fileSizeExceeded'));
      return false;
    }

    setError(null);
    return true;
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      handleFile(file);
    }
  };

  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      handleFile(file);
    }
  };

  const handleFile = (file: File) => {
    if (validateFile(file)) {
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);

      // Pass file to parent
      onFileSelect(file);
    }
  };

  const handleRemoveFile = () => {
    setPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="w-full">
      {!preview ? (
        <div
          className={`border-2 border-dashed rounded-xl p-8 transition-all duration-300 ${
            isDragging
              ? 'border-medical dark:border-medical-light bg-medical/5 dark:bg-medical/10'
              : 'border-slate-200 dark:border-slate-700 hover:border-medical/50 dark:hover:border-medical-light/50 hover:bg-slate-50 dark:hover:bg-slate-800/50'
          } ${isLoading ? 'opacity-50 pointer-events-none' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="flex flex-col items-center justify-center space-y-4 text-center cursor-pointer">
            <div className="w-16 h-16 rounded-full bg-medical/10 dark:bg-medical/20 flex items-center justify-center">
              <Upload className="h-8 w-8 text-medical dark:text-medical-light" strokeWidth={1.5} />
            </div>
            <div>
              <h3 className="text-lg font-medium text-slate-800 dark:text-white">
                {t('classification.uploadScan')}
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                {t('scans.uploadInstructions')}
              </p>
              <p className="text-xs text-slate-400 dark:text-slate-500 mt-2">
                {t('scans.supportedFormats')}
              </p>
            </div>
          </div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileInputChange}
            accept="image/*"
            className="hidden"
            disabled={isLoading}
          />
        </div>
      ) : (
        <div className="relative rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm">
          <div className="absolute top-2 right-2 z-10">
            <button
              onClick={handleRemoveFile}
              className="p-1.5 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm rounded-full text-slate-600 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-700 hover:text-red-500 dark:hover:text-red-400 transition-colors shadow-sm"
              disabled={isLoading}
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          <div className="aspect-square max-h-[400px] overflow-hidden">
            <img
              src={preview}
              alt="MRI Scan Preview"
              className="w-full h-full object-cover"
            />
          </div>
          <div className="p-3 text-center bg-slate-50 dark:bg-slate-700 border-t border-slate-100 dark:border-slate-600">
            <p className="text-sm text-slate-600 dark:text-slate-300 font-medium">
              {isLoading ? t('scans.processingImage') : t('scans.imageReady')}
            </p>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg flex items-center gap-2 text-red-700 dark:text-red-400 text-sm">
          <AlertCircle className="h-5 w-5" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};

export default UploadArea;
