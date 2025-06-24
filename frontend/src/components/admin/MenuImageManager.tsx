import React from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  CircularProgress
} from '@mui/material';
import { useQuery } from 'react-query';
import { restaurantApi } from '@services/api';
import ImageUpload from './ImageUpload';

interface MenuImageManagerProps {
  restaurantSlug: string;
}

const MenuImageManager: React.FC<MenuImageManagerProps> = ({ restaurantSlug }) => {
  const { data: restaurant } = useQuery(
    ['restaurant', restaurantSlug],
    () => restaurantApi.getBySlug(restaurantSlug),
    { enabled: !!restaurantSlug }
  );

  const { data: menu, isLoading, refetch } = useQuery(
    ['menu', restaurantSlug],
    () => restaurantApi.getMenu(restaurantSlug),
    { enabled: !!restaurantSlug }
  );

  const handleUploadSuccess = () => {
    // Refresh menu data after successful upload
    refetch();
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!menu || !(menu as any).categories) {
    return (
      <Container>
        <Typography sx={{ py: 4 }}>
          No menu items available.
        </Typography>
      </Container>
    );
  }

  // Flatten all menu items from all categories
  const allItems = (menu as any).categories.reduce((acc: any[], category: any) => {
    if (category.items) {
      acc.push(...category.items);
    }
    return acc;
  }, []);

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Menu Image Manager
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Upload and manage images for menu items at {(restaurant as any)?.name || restaurantSlug}
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {allItems.map((item: any) => (
          <Grid item xs={12} md={6} key={item.id}>
            <ImageUpload
              restaurantId={(restaurant as any)?.id || ''}
              itemId={item.id}
              itemName={item.name}
              currentImageUrl={item.image_url}
              onUploadSuccess={handleUploadSuccess}
            />
          </Grid>
        ))}
      </Grid>

      {allItems.length === 0 && (
        <Typography variant="body1" sx={{ py: 4, textAlign: 'center' }}>
          No menu items found. Please add menu items first.
        </Typography>
      )}
    </Container>
  );
};

export default MenuImageManager;