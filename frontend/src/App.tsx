import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline, Box } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Header from './components/Header';
import BuilderPage from './pages/BuilderPage';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#f97316', 
      light: '#fdba74',
      dark: '#c2410c',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#10b981', 
    },
    background: {
      default: '#121212', 
      paper: '#1e1e1e', 
    },
    text: {
      primary: '#f3f4f6', 
      secondary: '#9ca3af', 
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
  shape: {
    borderRadius: 8,
  },
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={darkTheme}>
        <CssBaseline />
        <BrowserRouter>
          <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: 'background.default' }}>
            <Header />
            <Box component="main" sx={{ flex: 1, p: { xs: 2, sm: 3 } }}>
              <Routes>
                <Route path="/" element={<BuilderPage />} />
              </Routes>
            </Box>
          </Box>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App;
