import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Grid, 
  Chip,
  Container,
  CircularProgress
} from '@mui/material';
import { useQuery } from 'react-query';
import { restaurantApi } from '@services/api';
import MenuItemAIPopup from './MenuItemAIPopup';

interface MenuDisplayProps {
  restaurantSlug: string;
  onAIChat?: (question: string, menuItem?: any, context?: any) => void;
}

const MenuDisplay: React.FC<MenuDisplayProps> = ({ restaurantSlug, onAIChat }) => {
  const [aiPopupAnchor, setAiPopupAnchor] = useState<HTMLElement | null>(null);
  const [selectedMenuItem, setSelectedMenuItem] = useState<any | null>(null);
  const [, ] = useState<ReturnType<typeof setTimeout> | null>(null);
  const { data: menu, isLoading, error } = useQuery(
    ['menu', restaurantSlug],
    () => restaurantApi.getMenu(restaurantSlug),
    {
      enabled: !!restaurantSlug
    }
  );

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container>
        <Typography color="error" sx={{ py: 4 }}>
          Error loading menu. Please try again.
        </Typography>
      </Container>
    );
  }

  if (!menu || !(menu as any).categories || (menu as any).categories.length === 0) {
    return (
      <Container>
        <Typography sx={{ py: 4 }}>
          No menu items available.
        </Typography>
      </Container>
    );
  }

  // Use categories directly from API response
  const itemsByCategory = (menu as any).categories.reduce((acc: any, category: any) => {
    if (category.items && category.items.length > 0) {
      acc[category.name] = category.items;
    }
    return acc;
  }, {});

  return (
    <Box sx={{ 
      background: 'linear-gradient(135deg, #FFF9E6 0%, #FFF0F5 50%, #F0F8FF 100%)',
      minHeight: '100vh',
      py: 4
    }}>
    <Container maxWidth="lg">
      {Object.entries(itemsByCategory).map(([categoryName, items]: [string, any]) => (
        <Box key={categoryName} sx={{ mb: 6 }}>
          <Typography 
            variant="h4" 
            component="h3" 
            gutterBottom 
            sx={{ 
              mb: 3,
              fontWeight: 700,
              color: '#8B4513',
              textAlign: 'center',
              fontSize: { xs: '1.8rem', md: '2.2rem' },
              position: 'relative',
              '&::after': {
                content: '""',
                position: 'absolute',
                bottom: '-8px',
                left: '50%',
                transform: 'translateX(-50%)',
                width: '80px',
                height: '4px',
                background: 'linear-gradient(90deg, #FF6B9D, #FFD93D)',
                borderRadius: '2px'
              }
            }}
          >
            {categoryName === 'Signature Cookies' ? '🍪 Signature Cookies' : 
             categoryName === 'Specialty Cookies' ? '✨ Specialty Cookies' :
             categoryName === 'Modifiers' ? '🎆 Sweet Add-Ons' : categoryName}
          </Typography>
          
          <Grid container spacing={3}>
            {items.map((item: any, index: number) => {
              // Fun colors for each card
              const cardColors = [
                { bg: 'linear-gradient(135deg, #FFE4E1 0%, #FFC0CB 100%)', accent: '#FF6B9D' },
                { bg: 'linear-gradient(135deg, #FFF8DC 0%, #FFE4B5 100%)', accent: '#FF8E53' },
                { bg: 'linear-gradient(135deg, #F0F8FF 0%, #E6E6FA 100%)', accent: '#9370DB' },
                { bg: 'linear-gradient(135deg, #F5FFFA 0%, #98FB98 100%)', accent: '#32CD32' },
                { bg: 'linear-gradient(135deg, #FFFACD 0%, #F0E68C 100%)', accent: '#FFD700' },
                { bg: 'linear-gradient(135deg, #FFE4E1 0%, #FFDAB9 100%)', accent: '#FF7F50' }
              ];
              const colorScheme = cardColors[index % cardColors.length];
              
              return (
              <Grid item xs={12} md={6} key={item.id}>
                <Card 
                  sx={{ 
                    height: '100%',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease-in-out',
                    position: 'relative',
                    background: colorScheme.bg,
                    border: `3px solid ${colorScheme.accent}`,
                    borderRadius: '16px',
                    '&:hover': {
                      transform: 'translateY(-8px) scale(1.02)',
                      boxShadow: `0 12px 40px rgba(0, 0, 0, 0.15)`,
                      borderColor: colorScheme.accent,
                    }
                  }}
                  onClick={(e) => {
                    // Toggle popup on click instead of hover
                    if (aiPopupAnchor && selectedMenuItem?.id === item.id) {
                      setAiPopupAnchor(null);
                      setSelectedMenuItem(null);
                    } else {
                      setAiPopupAnchor(e.currentTarget);
                      setSelectedMenuItem(item);
                    }
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Typography 
                        variant="h5" 
                        component="h4"
                        sx={{ 
                          fontWeight: 700,
                          color: '#8B4513',
                          fontSize: '1.4rem'
                        }}
                      >
                        {item.name}
                      </Typography>
                      <Box
                        sx={{
                          bgcolor: colorScheme.accent,
                          color: 'white',
                          px: 2,
                          py: 1,
                          borderRadius: '12px',
                          fontWeight: 700,
                          fontSize: '1.1rem',
                          boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
                        }}
                      >
                        ${item.price}
                      </Box>
                    </Box>
                    
                    <Typography 
                      variant="body1" 
                      sx={{ 
                        mb: 2,
                        color: '#5D4037',
                        lineHeight: 1.6,
                        fontSize: '1rem'
                      }}
                    >
                      {item.description}
                    </Typography>
                    
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                      {item.is_signature && (
                        <Chip 
                          label="⭐ Signature" 
                          sx={{
                            bgcolor: '#FFD700',
                            color: '#8B4513',
                            fontWeight: 600,
                            '& .MuiChip-label': { px: 1 }
                          }}
                          size="small" 
                        />
                      )}
                      <Chip 
                        label="🍪 Fresh Baked" 
                        sx={{
                          bgcolor: colorScheme.accent,
                          color: 'white',
                          fontWeight: 600,
                          '& .MuiChip-label': { px: 1 }
                        }}
                        size="small" 
                      />
                    </Box>
                    
                    {item.allergen_info && item.allergen_info.length > 0 && (
                      <Typography 
                        variant="caption" 
                        sx={{
                          color: '#8B4513',
                          fontWeight: 500,
                          fontSize: '0.8rem'
                        }}
                      >
                        🚨 Contains: {item.allergen_info.join(', ')}
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>
              );
            })}
          </Grid>
        </Box>
      ))}
      
      {/* AI Popup */}
      <MenuItemAIPopup
        anchorEl={aiPopupAnchor}
        open={Boolean(aiPopupAnchor && selectedMenuItem)}
        onClose={() => {
          setAiPopupAnchor(null);
          setSelectedMenuItem(null);
        }}
        menuItem={selectedMenuItem || {}}
        onAskAI={(question, menuItem) => {
          console.log('MenuDisplay: AI button clicked, question:', question);
          if (onAIChat) {
            console.log('MenuDisplay: Calling onAIChat with question and menu item context');
            onAIChat(question, menuItem, { 
              source: 'menu_item_popup',
              menu_item: menuItem 
            });
          } else {
            console.warn('MenuDisplay: onAIChat callback is not available');
          }
        }}
      />
    </Container>
    </Box>
  );
};

export default MenuDisplay;