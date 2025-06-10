import React from 'react';
import { Box, Typography, Chip, Container } from '@mui/material';
import { Restaurant } from '@types/index';

interface RestaurantHeaderProps {
  restaurant: Restaurant;
}

const RestaurantHeader: React.FC<RestaurantHeaderProps> = ({ restaurant }) => {
  return (
    <Box sx={{ 
      background: 'linear-gradient(135deg, #FF6B9D 0%, #FF8E53 50%, #FFD93D 100%)',
      color: 'white', 
      py: 6,
      position: 'relative',
      overflow: 'hidden',
      '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'url("data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.1"%3E%3Ccircle cx="7" cy="7" r="3"/%3E%3Ccircle cx="27" cy="7" r="3"/%3E%3Ccircle cx="47" cy="7" r="3"/%3E%3Ccircle cx="7" cy="27" r="3"/%3E%3Ccircle cx="27" cy="27" r="3"/%3E%3Ccircle cx="47" cy="27" r="3"/%3E%3Ccircle cx="7" cy="47" r="3"/%3E%3Ccircle cx="27" cy="47" r="3"/%3E%3Ccircle cx="47" cy="47" r="3"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
        pointerEvents: 'none'
      }
    }}>
      <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
        <Typography 
          variant="h2" 
          component="h1" 
          gutterBottom
          sx={{ 
            fontWeight: 800,
            fontSize: { xs: '2.5rem', md: '3.5rem' },
            textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
            letterSpacing: '-0.02em'
          }}
        >
          🍪 {restaurant.name}
        </Typography>
        <Typography 
          variant="h5" 
          sx={{ 
            mb: 3, 
            fontWeight: 500,
            textShadow: '1px 1px 2px rgba(0,0,0,0.3)',
            maxWidth: '600px'
          }}
        >
          {restaurant.description}
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
          <Chip 
            label={`🎯 ${restaurant.cuisine_type}`}
            sx={{ 
              bgcolor: 'rgba(255,255,255,0.9)',
              color: '#FF6B9D',
              fontWeight: 600,
              fontSize: '1rem',
              px: 2,
              py: 1,
              height: 'auto',
              '& .MuiChip-label': { px: 1 }
            }} 
          />
          <Chip 
            label="✨ Fresh Baked Daily"
            sx={{ 
              bgcolor: 'rgba(255,212,61,0.9)',
              color: '#8B4513',
              fontWeight: 600,
              fontSize: '1rem',
              px: 2,
              py: 1,
              height: 'auto',
              '& .MuiChip-label': { px: 1 }
            }} 
          />
          <Chip 
            label="🔥 Warm & Gooey"
            sx={{ 
              bgcolor: 'rgba(255,142,83,0.9)',
              color: 'white',
              fontWeight: 600,
              fontSize: '1rem',
              px: 2,
              py: 1,
              height: 'auto',
              '& .MuiChip-label': { px: 1 }
            }} 
          />
        </Box>
      </Container>
    </Box>
  );
};

export default RestaurantHeader;