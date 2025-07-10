import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  CardMedia,
  Grid, 
  Chip,
  Container,
  CircularProgress
} from '@mui/material';
import { useQuery } from 'react-query';
import { restaurantApi } from '@services/api';
import MenuItemAIPopup from './MenuItemAIPopup';
import { chipCookiesMenu } from '@/data/chipCookiesMenu';
import { useRestaurantTheme } from '@/hooks/useRestaurantTheme';

interface MenuDisplayProps {
  restaurantSlug: string;
  onAIChat?: (question: string, menuItem?: any, context?: any) => void;
}

const MenuDisplay: React.FC<MenuDisplayProps> = ({ restaurantSlug, onAIChat }) => {
  const [aiPopupAnchor, setAiPopupAnchor] = useState<HTMLElement | null>(null);
  const [selectedMenuItem, setSelectedMenuItem] = useState<any | null>(null);
  const [, ] = useState<ReturnType<typeof setTimeout> | null>(null);
  const restaurantTheme = useRestaurantTheme(restaurantSlug);
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
      background: `linear-gradient(135deg, ${restaurantTheme.background} 0%, ${restaurantTheme.accent}40 50%, ${restaurantTheme.secondary}20 100%)`,
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
              color: restaurantTheme.primary,
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
                background: restaurantTheme.gradients.button,
                borderRadius: '2px'
              }
            }}
          >
            {categoryName === 'Classic Chips' ? '🍪 Classic Chips' : 
             categoryName === 'Specialty Chips' ? '✨ Specialty Chips' :
             categoryName === 'Beverages' ? '🥛 Beverages' : 
             categoryName === 'Signature Cookies' ? '🍪 Signature Cookies' : 
             categoryName === 'Specialty Cookies' ? '✨ Specialty Cookies' :
             categoryName === 'Modifiers' ? '🎆 Sweet Add-Ons' : categoryName}
          </Typography>
          
          <Grid container spacing={3}>
            {items.map((item: any, index: number) => {
              // Use restaurant theme colors
              const colorScheme = { 
                bg: `linear-gradient(135deg, ${restaurantTheme.background} 0%, ${restaurantTheme.accent} 100%)`, 
                accent: restaurantTheme.primary,
                hover: restaurantTheme.secondary
              };
              
              return (
              <Grid item xs={12} md={6} key={item.id}>
                <Card 
                  sx={{ 
                    height: '100%',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease-in-out',
                    position: 'relative',
                    background: colorScheme.bg,
                    border: `2px solid ${colorScheme.accent}30`,
                    borderRadius: '12px',
                    boxShadow: `0 4px 12px ${colorScheme.accent}30`,
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: `0 8px 24px ${colorScheme.accent}40`,
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
                  {/* Menu Item Image */}
                  {item.image_url && (
                    <Box sx={{ 
                      position: 'relative', 
                      height: '200px', 
                      overflow: 'hidden',
                      borderRadius: '12px 12px 0 0'
                    }}>
                      <CardMedia
                        component="img"
                        height="200"
                        image={item.image_url.startsWith('http') 
                          ? item.image_url 
                          : item.image_url
                        }
                        alt={`${item.name} - ${item.description || 'Menu item'}`}
                        loading="lazy"
                        sx={{
                          objectFit: 'cover',
                          width: '100%',
                          height: '100%',
                          transition: 'all 0.3s ease',
                          '&:hover': {
                            transform: 'scale(1.08)',
                            filter: 'brightness(1.1)',
                          }
                        }}
                        onError={(e) => {
                          // Replace with placeholder image
                          const target = e.target as HTMLImageElement;
                          target.src = 'data:image/svg+xml,' + encodeURIComponent(`
                            <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
                              <rect width="100%" height="100%" fill="${colorScheme.accent}20"/>
                              <text x="50%" y="50%" text-anchor="middle" dy=".3em" 
                                    font-family="Arial" font-size="16" fill="${colorScheme.accent}">
                                🍪 ${item.name}
                              </text>
                            </svg>
                          `);
                          target.alt = `${item.name} - Image unavailable`;
                        }}
                      />
                      
                      {/* Image overlay for better text readability if needed */}
                      {item.is_signature && (
                        <Box sx={{
                          position: 'absolute',
                          top: 8,
                          right: 8,
                          bgcolor: '#FFD700',
                          color: '#8B4513',
                          px: 1,
                          py: 0.5,
                          borderRadius: '8px',
                          fontSize: '12px',
                          fontWeight: 600,
                          boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                        }}>
                          ⭐ Signature
                        </Box>
                      )}
                    </Box>
                  )}
                  
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Typography 
                        variant="h5" 
                        component="h4"
                        sx={{ 
                          fontWeight: 700,
                          color: restaurantTheme.primary,
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
                          boxShadow: `0 2px 8px ${colorScheme.accent}40`
                        }}
                      >
                        ${item.price}
                      </Box>
                    </Box>
                    
                    <Typography 
                      variant="body1" 
                      sx={{ 
                        mb: 2,
                        color: restaurantTheme.text,
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
                          color: restaurantTheme.primary,
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
        restaurantSlug={restaurantSlug}
        onAskAI={(question, menuItem) => {
          if (onAIChat) {
            onAIChat(question, menuItem, { 
              source: 'menu_item_popup',
              menu_item: menuItem 
            });
          } else {
          }
        }}
      />
    </Container>
    </Box>
  );
};

export default MenuDisplay;