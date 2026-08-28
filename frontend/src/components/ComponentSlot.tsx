import React, { type ReactNode } from 'react';
import { Card, CardContent, Typography, IconButton, Box, Chip } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import CloseIcon from '@mui/icons-material/Close';
import type { ComponentBase } from '../types/api';

export interface ComponentSlotProps {
  label: string;
  icon: ReactNode;
  component: ComponentBase | null;
  onSelect: () => void;
  onRemove: () => void;
}

export const ComponentSlot: React.FC<ComponentSlotProps> = ({
  label,
  icon,
  component,
  onSelect,
  onRemove,
}) => {
  if (!component) {
    return (
      <Card
        variant="outlined"
        sx={{
          borderStyle: 'dashed',
          borderWidth: 2,
          borderColor: 'rgba(255, 255, 255, 0.2)',
          backgroundColor: 'rgba(30, 41, 59, 0.4)',
          borderRadius: 2,
          transition: 'all 0.2s ease-in-out',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: 170,
          p: 2,
          cursor: 'pointer',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'rgba(249, 115, 22, 0.08)',
            transform: 'translateY(-2px)',
          },
        }}
        onClick={onSelect}
      >
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1 }}>
          <Box sx={{ color: 'text.secondary', display: 'flex', alignItems: 'center', gap: 1 }}>
            {icon}
            <Typography variant="subtitle1" color="text.primary" sx={{ fontWeight: 600 }}>
              {label}
            </Typography>
          </Box>
          <IconButton
            color="primary"
            aria-label={`Add ${label}`}
            onClick={(e) => {
              e.stopPropagation();
              onSelect();
            }}
            sx={{
              backgroundColor: 'primary.main',
              color: 'primary.contrastText',
              width: 42,
              height: 42,
              '&:hover': {
                backgroundColor: 'primary.dark',
              },
            }}
          >
            <AddIcon />
          </IconButton>
          <Typography variant="caption" color="text.secondary">
            Click to select component
          </Typography>
        </Box>
      </Card>
    );
  }

  const formattedPrice = Number(component.price || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  return (
    <Card
      elevation={2}
      sx={{
        backgroundColor: '#1e1e1e',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: 2,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        minHeight: 170,
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          boxShadow: 6,
          borderColor: 'primary.light',
          transform: 'translateY(-2px)',
        },
      }}
    >
      <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column', p: 2, '&:last-child': { pb: 2 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'primary.main' }}>
            {icon}
            <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontWeight: 700 }}>
              {label}
            </Typography>
          </Box>
          <IconButton
            size="small"
            aria-label={`Remove ${label}`}
            onClick={(e) => {
              e.stopPropagation();
              onRemove();
            }}
            sx={{
              color: 'text.secondary',
              p: 0.5,
              '&:hover': {
                color: 'error.main',
                backgroundColor: 'rgba(244, 67, 54, 0.12)',
              },
            }}
          >
            <CloseIcon fontSize="small" />
          </IconButton>
        </Box>

        <Typography
          variant="subtitle1"
          sx={{
            fontWeight: 600,
            mt: 0.5,
            color: 'text.primary',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            minHeight: '2.8em',
          }}
          title={component.name}
        >
          {component.name}
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mt: 'auto', pt: 1.5 }}>
          <Chip
            label={component.brand}
            size="small"
            variant="outlined"
            sx={{
              borderColor: 'rgba(255, 255, 255, 0.2)',
              color: 'text.secondary',
              fontWeight: 500,
            }}
          />
          <Typography variant="h6" color="primary.light" sx={{ fontWeight: 700 }}>
            {formattedPrice} zł
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ComponentSlot;
