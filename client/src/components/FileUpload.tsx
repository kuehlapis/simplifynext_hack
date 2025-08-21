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
    <Card className="p-8 bg-gradient-surface border-2 border-dashed border-border hover:border-primary/50 transition-colors">
      <div {...getRootProps()} className="cursor-pointer text-center">
        <input {...getInputProps()} />
        
        {uploadedFile ? (
          <div className="space-y-4">
            <CheckCircle className="w-12 h-12 text-success mx-auto" />
            <div>
              <h3 className="text-lg font-semibold text-foreground">File Ready</h3>
              <p className="text-muted-foreground">{uploadedFile.name}</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {isDragActive ? (
              <>
                <Upload className="w-12 h-12 text-primary mx-auto animate-bounce" />
                <h3 className="text-lg font-semibold text-primary">Drop your file here</h3>
              </>
            ) : (
              <>
                <FileText className="w-12 h-12 text-muted-foreground mx-auto" />
                <div>
                  <h3 className="text-lg font-semibold text-foreground">Upload Tenant Agreement</h3>
                  <p className="text-muted-foreground">Drag & drop a PDF or Markdown file here</p>
                </div>
                <Button variant="outline" className="mt-4">
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