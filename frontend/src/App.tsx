import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';
import { Toaster } from 'react-hot-toast';

// Pages
import RestaurantPage from '@pages/RestaurantPage';
import AdminDashboard from '@pages/AdminDashboard';
import NotFoundPage from '@pages/NotFoundPage';
import LandingPage from '@pages/LandingPage';

// Components
import ErrorBoundary from '@components/common/ErrorBoundary';
import LoadingProvider from '@components/common/LoadingProvider';

// Store
import { useThemeStore } from '@store/themeStore';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  const { mode, primaryColor } = useThemeStore();

  // Create MUI theme
  const theme = createTheme({
    palette: {
      mode,
      primary: {
        main: primaryColor,
      },
      secondary: {
        main: mode === 'light' ? '#f50057' : '#ff4081',
      },
      background: {
        default: mode === 'light' ? '#f5f5f5' : '#121212',
        paper: mode === 'light' ? '#ffffff' : '#1e1e1e',
      },
    },
    typography: {
      fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
      h1: {
        fontWeight: 600,
      },
      h2: {
        fontWeight: 600,
      },
      h3: {
        fontWeight: 600,
      },
      h4: {
        fontWeight: 500,
      },
      h5: {
        fontWeight: 500,
      },
      h6: {
        fontWeight: 500,
      },
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            textTransform: 'none',
            fontWeight: 500,
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 12,
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          },
        },
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            '& .MuiOutlinedInput-root': {
              borderRadius: 8,
            },
          },
        },
      },
    },
  });

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <LoadingProvider>
            <Router>
              <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
                <Routes>
                  {/* Landing page */}
                  <Route path="/" element={<LandingPage />} />
                  
                  {/* Restaurant pages */}
                  <Route path="/r/:restaurantSlug" element={<RestaurantPage />} />
                  <Route path="/r/:restaurantSlug/menu" element={<RestaurantPage />} />
                  <Route path="/r/:restaurantSlug/chat" element={<RestaurantPage />} />
                  
                  {/* Admin routes */}
                  <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
                  <Route path="/admin/*" element={<AdminDashboard />} />
                  
                  {/* Error pages */}
                  <Route path="/404" element={<NotFoundPage />} />
                  <Route path="*" element={<Navigate to="/404" replace />} />
                </Routes>
              </Box>
            </Router>
          </LoadingProvider>
          
          {/* Toast notifications */}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: theme.palette.background.paper,
                color: theme.palette.text.primary,
                borderRadius: 8,
              },
              success: {
                iconTheme: {
                  primary: theme.palette.success.main,
                  secondary: theme.palette.success.contrastText,
                },
              },
              error: {
                iconTheme: {
                  primary: theme.palette.error.main,
                  secondary: theme.palette.error.contrastText,
                },
              },
            }}
          />
          
          {/* React Query DevTools */}
          {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;