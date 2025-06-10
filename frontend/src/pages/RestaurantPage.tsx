import React, { useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { Box, Container, Grid, Paper, Typography, Skeleton } from '@mui/material';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

// Components
import RestaurantHeader from '@components/restaurant/RestaurantHeader';
import MenuDisplay from '@components/menu/MenuDisplay';
import FloatingAIAssistant from '@components/chat/FloatingAIAssistant';
import ErrorMessage from '@components/common/ErrorMessage';

// Services
import { restaurantApi } from '@services/api';

// Store
import { useThemeStore } from '@store/themeStore';

// Types
import { Restaurant } from '@types/index';

const RestaurantPage: React.FC = () => {
  const { restaurantSlug } = useParams<{ restaurantSlug: string }>();
  const location = useLocation();
  const { setRestaurantTheme } = useThemeStore();
  const [chatSendMessage, setChatSendMessage] = React.useState<((message: string) => void) | null>(null);

  // Chat is now floating, menu is always shown

  // Fetch restaurant data
  const {
    data: restaurant,
    isLoading: restaurantLoading,
    error: restaurantError,
  } = useQuery<Restaurant>(
    ['restaurant', restaurantSlug],
    () => restaurantApi.getBySlug(restaurantSlug!),
    {
      enabled: !!restaurantSlug,
      onSuccess: (data) => {
        // Update theme based on restaurant branding
        setRestaurantTheme(data);
      },
      onError: (error: Error) => {
        toast.error(error.message || 'Failed to load restaurant');
      },
    }
  );

  // Fetch avatar configuration
  const {
    data: avatarConfig,
    isLoading: avatarLoading,
  } = useQuery(
    ['avatar', restaurantSlug],
    () => restaurantApi.getAvatarConfig(restaurantSlug!),
    {
      enabled: !!restaurantSlug,
    }
  );

  // Set page title
  useEffect(() => {
    if (restaurant) {
      document.title = `${restaurant.name} - Restaurant AI`;
    }
  }, [restaurant]);

  if (restaurantError) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <ErrorMessage 
          message="Restaurant not found" 
          description="The restaurant you're looking for doesn't exist or is currently unavailable."
        />
      </Container>
    );
  }

  if (restaurantLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <RestaurantHeaderSkeleton />
        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12} md={8}>
            <MenuSkeleton />
          </Grid>
          <Grid item xs={12} md={4}>
            <ChatSkeleton />
          </Grid>
        </Grid>
      </Container>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <Container maxWidth="lg" sx={{ py: 2 }}>
        {/* Restaurant Header */}
        <RestaurantHeader 
          restaurant={restaurant!} 
        />

        {/* Main Content - Full width menu */}
        <Box sx={{ mt: 2 }}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <MenuDisplay 
              restaurantSlug={restaurantSlug!} 
              onAIChat={(question) => {
                if (chatSendMessage) {
                  chatSendMessage(question);
                }
              }}
            />
          </motion.div>
        </Box>

        {/* Floating AI Assistant */}
        <FloatingAIAssistant
          restaurantSlug={restaurantSlug!}
          onChatReady={(sendMessage) => setChatSendMessage(() => sendMessage)}
        />
      </Container>
    </motion.div>
  );
};

// Skeleton components for loading states
const RestaurantHeaderSkeleton: React.FC = () => (
  <Paper sx={{ p: 3, mb: 3 }}>
    <Skeleton variant="text" width="40%" height={40} />
    <Skeleton variant="text" width="60%" height={24} sx={{ mt: 1 }} />
    <Skeleton variant="rectangular" width="100%" height={60} sx={{ mt: 2, borderRadius: 1 }} />
  </Paper>
);

const MenuSkeleton: React.FC = () => (
  <Paper sx={{ p: 3 }}>
    <Skeleton variant="text" width="30%" height={32} />
    <Box sx={{ mt: 2 }}>
      {[...Array(5)].map((_, index) => (
        <Box key={index} sx={{ mb: 3 }}>
          <Skeleton variant="rectangular" width="100%" height={120} sx={{ borderRadius: 1 }} />
          <Skeleton variant="text" width="40%" height={24} sx={{ mt: 1 }} />
          <Skeleton variant="text" width="80%" height={20} />
        </Box>
      ))}
    </Box>
  </Paper>
);

const ChatSkeleton: React.FC = () => (
  <Paper sx={{ p: 3, height: '100%' }}>
    <Skeleton variant="text" width="50%" height={32} />
    <Box sx={{ mt: 2 }}>
      {[...Array(4)].map((_, index) => (
        <Box key={index} sx={{ mb: 2 }}>
          <Skeleton variant="rectangular" width="80%" height={40} sx={{ borderRadius: 2, mb: 1 }} />
          <Skeleton variant="rectangular" width="60%" height={40} sx={{ borderRadius: 2, ml: 'auto' }} />
        </Box>
      ))}
    </Box>
  </Paper>
);

export default RestaurantPage;