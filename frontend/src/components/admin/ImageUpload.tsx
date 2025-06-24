import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  CardActions
} from '@mui/material';
import { PhotoCamera } from '@mui/icons-material';
import { menuImageApi } from '@services/api';

interface ImageUploadProps {
  restaurantId: string;
  itemId: string;
  itemName: string;
  currentImageUrl?: string;
  onUploadSuccess?: (imageUrl: string) => void;
}

const ImageUpload: React.FC<ImageUploadProps> = ({
  restaurantId,
  itemId,
  itemName,
  currentImageUrl,
  onUploadSuccess
}) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file');
      return;
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await menuImageApi.uploadImage(restaurantId, itemId, file);
      setSuccess('Image uploaded successfully!');
      onUploadSuccess?.((response as any).image_url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Upload Image for "{itemName}"
        </Typography>

        {currentImageUrl && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Current Image:
            </Typography>
            <img
              src={currentImageUrl}
              alt={itemName}
              style={{
                maxWidth: '200px',
                maxHeight: '200px',
                objectFit: 'cover',
                borderRadius: '8px',
                border: '2px solid #ddd'
              }}
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = 'none';
              }}
            />
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}
      </CardContent>

      <CardActions>
        <Button
          variant="contained"
          component="label"
          startIcon={uploading ? <CircularProgress size={20} /> : <PhotoCamera />}
          disabled={uploading}
        >
          {uploading ? 'Uploading...' : 'Upload New Image'}
          <input
            type="file"
            accept="image/*"
            hidden
            onChange={handleFileUpload}
          />
        </Button>
      </CardActions>
    </Card>
  );
};

export default ImageUpload;