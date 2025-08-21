import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isProcessing: boolean;
}

export const FileUpload = ({ onFileSelect, isProcessing }: FileUploadProps) => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setUploadedFile(file);
      onFileSelect(file);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/markdown': ['.md'],
      'text/plain': ['.txt']
    },
    maxFiles: 1,
    disabled: isProcessing
  });

  return (
    <Card className="p-12 border-2 border-dashed border-border/50 shadow-medium hover:shadow-large transition-all duration-300 bg-gradient-hero animate-fade-in">
      <div {...getRootProps()} className={`cursor-pointer text-center transition-all duration-300 ${isDragActive ? 'scale-[1.02] bg-gradient-surface rounded-lg p-6' : ''}`}>
        <input {...getInputProps()} />
        
        {uploadedFile ? (
          <div className="space-y-6">
            <div className="relative mx-auto w-20 h-20 bg-gradient-to-r from-success to-success/80 rounded-2xl flex items-center justify-center shadow-medium animate-glow">
              <CheckCircle className="w-10 h-10 text-white" />
              <div className="absolute inset-0 bg-success/20 rounded-2xl blur-xl"></div>
            </div>
            <div>
              <h3 className="text-2xl font-bold text-foreground mb-2 bg-gradient-primary bg-clip-text text-transparent">File Ready</h3>
              <p className="text-muted-foreground text-lg">{uploadedFile.name}</p>
              <div className="mt-4 inline-flex items-center space-x-2 bg-success/10 px-4 py-2 rounded-full">
                <div className="w-2 h-2 bg-success rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-success">Ready for processing</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {isDragActive ? (
              <>
                <div className="relative mx-auto w-20 h-20 bg-gradient-primary rounded-2xl flex items-center justify-center shadow-glow animate-bounce">
                  <Upload className="w-10 h-10 text-primary-foreground" />
                  <div className="absolute inset-0 bg-gradient-primary rounded-2xl opacity-20 blur-xl"></div>
                </div>
                <h3 className="text-2xl font-bold text-primary animate-pulse">Drop your file here</h3>
              </>
            ) : (
              <>
                <div className="relative mx-auto w-20 h-20 bg-gradient-surface border-2 border-dashed border-border rounded-2xl flex items-center justify-center shadow-soft hover:shadow-medium transition-all duration-300">
                  <FileText className="w-10 h-10 text-muted-foreground" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-foreground mb-3 bg-gradient-primary bg-clip-text text-transparent">Upload Tenant Agreement</h3>
                  <p className="text-muted-foreground text-lg mb-6">Drag & drop a PDF or Markdown file here</p>
                  
                  <div className="text-sm text-muted-foreground space-y-2 bg-muted/30 rounded-lg p-4 inline-block mb-6">
                    <p className="flex items-center justify-center gap-2">
                      <span className="w-2 h-2 bg-success rounded-full"></span>
                      Supported formats: PDF, MD, TXT
                    </p>
                    <p className="flex items-center justify-center gap-2">
                      <span className="w-2 h-2 bg-primary rounded-full"></span>
                      Maximum file size: 10MB
                    </p>
                  </div>
                </div>
                <Button variant="outline" className="px-8 py-3 text-lg font-medium bg-gradient-primary text-primary-foreground border-0 hover:opacity-90 shadow-medium hover:shadow-large transition-all duration-300">
                  Choose File
                </Button>
              </>
            )}
          </div>
        )}
      </div>
    </Card>
  );
};