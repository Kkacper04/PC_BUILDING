import React, { useState, useMemo } from 'react';
import {
  Dialog,
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Slide,
  Box,
  Container,
  TextField,
  InputAdornment,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Skeleton,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import type { TransitionProps } from '@mui/material/transitions';
import type { ComponentBase } from '../types/api';

const Transition = React.forwardRef(function Transition(
  props: TransitionProps & {
    children: React.ReactElement<unknown>;
  },
  ref: React.Ref<unknown>,
) {
  return <Slide direction="up" ref={ref} {...props} />;
});

export interface SelectionModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  items: ComponentBase[];
  isLoading: boolean;
  onSelect: (item: ComponentBase) => void;
}

export const SelectionModal: React.FC<SelectionModalProps> = ({
  open,
  onClose,
  title,
  items = [],
  isLoading,
  onSelect,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredItems = useMemo(() => {
    if (!items || !Array.isArray(items)) return [];
    if (!searchTerm.trim()) return items;
    const term = searchTerm.toLowerCase();
    return items.filter(
      (item) =>
        item.name?.toLowerCase().includes(term) ||
        item.brand?.toLowerCase().includes(term) ||
        item.model?.toLowerCase().includes(term),
    );
  }, [items, searchTerm]);

  const handleClose = () => {
    setSearchTerm('');
    onClose();
  };

  const handleSelectItem = (item: ComponentBase) => {
    onSelect(item);
    handleClose();
  };

  return (
    <Dialog
      fullScreen
      open={open}
      onClose={handleClose}
      slots={{
        transition: Transition,
      }}
      slotProps={{
        paper: {
          sx: { backgroundColor: '#121212' }
        }
      }}
    >
      <AppBar
        sx={{
          position: 'sticky',
          top: 0,
          backgroundColor: '#1c1c1c',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          zIndex: 1100,
        }}
      >
        <Toolbar>
          <IconButton edge="start" color="inherit" onClick={handleClose} aria-label="close">
            <CloseIcon />
          </IconButton>
          <Typography sx={{ ml: 2, flex: 1, fontWeight: 700 }} variant="h6" component="div">
            {title}
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 4, flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Search Bar */}
        <Box sx={{ mb: 4 }}>
          <TextField
            fullWidth
            placeholder="Search by name, brand, or model..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            variant="outlined"
            slotProps={{
              input: {
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon color="action" />
                  </InputAdornment>
                ),
                endAdornment: searchTerm ? (
                  <InputAdornment position="end">
                    <IconButton size="small" onClick={() => setSearchTerm('')} aria-label="clear search">
                      <ClearIcon fontSize="small" />
                    </IconButton>
                  </InputAdornment>
                ) : null,
              },
            }}
            sx={{
              backgroundColor: '#1e1e1e',
              borderRadius: 2,
              '& .MuiOutlinedInput-root': {
                '& fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.12)',
                },
                '&:hover fieldset': {
                  borderColor: 'primary.main',
                },
              },
            }}
          />
        </Box>

        {/* Loading Skeletons */}
        {isLoading && (
          <Grid container spacing={3}>
            {Array.from({ length: 6 }).map((_, index) => (
              <Grid size={{ xs: 12, sm: 6, md: 4 }} key={index}>
                <Card
                  sx={{
                    height: '100%',
                    backgroundColor: '#1e1e1e',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: 2,
                    p: 2,
                  }}
                >
                  <Skeleton variant="text" width="40%" height={24} sx={{ mb: 1 }} />
                  <Skeleton variant="text" width="90%" height={32} sx={{ mb: 1 }} />
                  <Skeleton variant="text" width="60%" height={20} sx={{ mb: 2 }} />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
                    <Skeleton variant="text" width="30%" height={32} />
                    <Skeleton variant="rounded" width={80} height={36} />
                  </Box>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Items List */}
        {!isLoading && filteredItems.length > 0 && (
          <Grid container spacing={3}>
            {filteredItems.map((item) => {
              const formattedPrice = Number(item.price || 0).toLocaleString(undefined, {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              });

              return (
                <Grid size={{ xs: 12, sm: 6, md: 4 }} key={item.id}>
                  <Card
                    elevation={2}
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      backgroundColor: '#1e1e1e',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: 2,
                      transition: 'transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease',
                      '&:hover': {
                        transform: 'translateY(-3px)',
                        borderColor: 'primary.main',
                        boxShadow: 6,
                      },
                    }}
                  >
                    <CardContent sx={{ flex: 1, p: 2.5 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                        <Chip
                          label={item.brand}
                          size="small"
                          color="primary"
                          variant="outlined"
                          sx={{ fontWeight: 600, fontSize: '0.75rem' }}
                        />
                        <Typography variant="h6" sx={{ fontWeight: 700 }} color="primary.light">
                          {formattedPrice} zł
                        </Typography>
                      </Box>

                      <Typography
                        variant="subtitle1"
                        color="text.primary"
                        sx={{
                          fontWeight: 600,
                          mt: 1,
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                          minHeight: '3em',
                        }}
                        title={item.name}
                      >
                        {item.name}
                      </Typography>

                      {item.model && item.model !== item.name && (
                        <Typography variant="body2" color="text.secondary" noWrap sx={{ mt: 0.5 }}>
                          Model: {item.model}
                        </Typography>
                      )}
                    </CardContent>

                    <CardActions sx={{ p: 2.5, pt: 0, justifyContent: 'flex-end' }}>
                      <Button
                        variant="contained"
                        color="primary"
                        startIcon={<CheckCircleIcon />}
                        onClick={() => handleSelectItem(item)}
                        sx={{
                          fontWeight: 600,
                          textTransform: 'none',
                          borderRadius: 1.5,
                          px: 2.5,
                        }}
                      >
                        Select
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        )}

        {/* Empty Search / Empty Data state */}
        {!isLoading && filteredItems.length === 0 && (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              py: 8,
              textAlign: 'center',
            }}
          >
            <Typography variant="h6" color="text.secondary" gutterBottom>
              {searchTerm ? 'No components found matching your search.' : 'No components available.'}
            </Typography>
            {searchTerm && (
              <Button variant="outlined" color="primary" onClick={() => setSearchTerm('')} sx={{ mt: 2 }}>
                Clear Search
              </Button>
            )}
          </Box>
        )}
      </Container>
    </Dialog>
  );
};

export default SelectionModal;
