/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Container,
  Grid,
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Divider,
  Alert,
  AlertTitle,
  CircularProgress,
  Paper,
  Stack,
  Chip,
} from '@mui/material';
import MemoryIcon from '@mui/icons-material/Memory';
import DeveloperBoardIcon from '@mui/icons-material/DeveloperBoard';
import TvIcon from '@mui/icons-material/Tv';
import PowerIcon from '@mui/icons-material/Power';
import ComputerIcon from '@mui/icons-material/Computer';
import AcUnitIcon from '@mui/icons-material/AcUnit';
import StorageIcon from '@mui/icons-material/Storage';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RestartAltIcon from '@mui/icons-material/RestartAlt';

import { ComponentSlot } from '../components/ComponentSlot';
import { SelectionModal } from '../components/SelectionModal';
import { WattageCalculator } from '../components/WattageCalculator';
import { ShareBuildButton } from '../components/ShareBuildButton';
import { ExportBuildPDF } from '../components/ExportBuildPDF';
import {
  useCPUs,
  useMotherboards,
  useRAM,
  useGPUs,
  usePSUs,
  useCases,
  useCoolers,
  useStorage,
  useValidateBuild,
} from '../api/queries';
import { useBuildStore } from '../store/buildStore';
import type { ComponentBase, ComponentType } from '../types/api';
import { decodeBuildFromUrl, hasBuildParams } from '../utils/shareBuild';
import {
  fetchCPU,
  fetchMotherboard,
  fetchRAMItem,
  fetchGPU,
  fetchPSU,
  fetchCase,
  fetchCooler,
  fetchStorageItem,
} from '../api/queries';

interface SlotConfig {
  type: ComponentType;
  label: string;
  modalTitle: string;
  icon: React.ReactNode;
  component: ComponentBase | null;
  items: ComponentBase[];
  isLoading: boolean;
}

export const BuilderPage: React.FC = () => {
  const [activeModal, setActiveModal] = useState<ComponentType | null>(null);
  const location = useLocation();

  // Store access
  const store = useBuildStore();
  const cpu = store.cpu;
  const motherboard = store.motherboard;
  const ram = store.ram;
  const gpu = store.gpu;
  const psu = store.psu;
  const pcCase = store.pcCase;
  const cooler = store.cooler;
  const storage = store.storage;

  // Load shared build from URL parameters
  useEffect(() => {
    if (!hasBuildParams(location.search)) return;
    const ids = decodeBuildFromUrl(location.search);
    const load = async () => {
      try {
        if (ids.cpu) store.setComponent('cpu', await fetchCPU(ids.cpu) as any);
        if (ids.motherboard) store.setComponent('motherboard', await fetchMotherboard(ids.motherboard) as any);
        if (ids.ram) store.setComponent('ram', await fetchRAMItem(ids.ram) as any);
        if (ids.gpu) store.setComponent('gpu', await fetchGPU(ids.gpu) as any);
        if (ids.psu) store.setComponent('psu', await fetchPSU(ids.psu) as any);
        if (ids.case) store.setComponent('case', await fetchCase(ids.case) as any);
        if (ids.cooler) store.setComponent('cooler', await fetchCooler(ids.cooler) as any);
        if (ids.storage) store.setComponent('storage', await fetchStorageItem(ids.storage) as any);
      } catch (err) {
        console.error('Failed to load shared build:', err);
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.search]);

  // React Query hooks for each component type
  const cpusQuery = useCPUs();
  const motherboardsQuery = useMotherboards();
  const ramQuery = useRAM();
  const gpusQuery = useGPUs();
  const psusQuery = usePSUs();
  const casesQuery = useCases();
  const coolersQuery = useCoolers();
  const storageQuery = useStorage();

  // Validation mutation
  const validateBuildMutation = useValidateBuild();

  // Config array mapping each ComponentType to label, icon, and query data
  const slotConfigs: SlotConfig[] = [
    {
      type: 'cpu' as ComponentType,
      label: 'Processor',
      modalTitle: 'Select a Processor (CPU)',
      icon: <MemoryIcon fontSize="medium" />,
      component: cpu,
      items: (cpusQuery.data as ComponentBase[]) || [],
      isLoading: cpusQuery.isLoading,
    },
    {
      type: 'motherboard' as ComponentType,
      label: 'Motherboard',
      modalTitle: 'Select a Motherboard',
      icon: <DeveloperBoardIcon fontSize="medium" />,
      component: motherboard,
      items: (motherboardsQuery.data as ComponentBase[]) || [],
      isLoading: motherboardsQuery.isLoading,
    },
    {
      type: 'ram' as ComponentType,
      label: 'Memory (RAM)',
      modalTitle: 'Select Memory (RAM)',
      icon: <MemoryIcon fontSize="medium" />,
      component: ram,
      items: (ramQuery.data as ComponentBase[]) || [],
      isLoading: ramQuery.isLoading,
    },
    {
      type: 'gpu' as ComponentType,
      label: 'Graphics Card',
      modalTitle: 'Select a Graphics Card (GPU)',
      icon: <TvIcon fontSize="medium" />,
      component: gpu,
      items: (gpusQuery.data as ComponentBase[]) || [],
      isLoading: gpusQuery.isLoading,
    },
    {
      type: 'psu' as ComponentType,
      label: 'Power Supply',
      modalTitle: 'Select a Power Supply (PSU)',
      icon: <PowerIcon fontSize="medium" />,
      component: psu,
      items: (psusQuery.data as ComponentBase[]) || [],
      isLoading: psusQuery.isLoading,
    },
    {
      type: 'case' as ComponentType,
      label: 'PC Case',
      modalTitle: 'Select a PC Case',
      icon: <ComputerIcon fontSize="medium" />,
      component: pcCase,
      items: (casesQuery.data as ComponentBase[]) || [],
      isLoading: casesQuery.isLoading,
    },
    {
      type: 'cooler' as ComponentType,
      label: 'CPU Cooler',
      modalTitle: 'Select a CPU Cooler',
      icon: <AcUnitIcon fontSize="medium" />,
      component: cooler,
      items: (coolersQuery.data as ComponentBase[]) || [],
      isLoading: coolersQuery.isLoading,
    },
    {
      type: 'storage' as ComponentType,
      label: 'Storage Drive',
      modalTitle: 'Select Storage (SSD / HDD)',
      icon: <StorageIcon fontSize="medium" />,
      component: storage,
      items: (storageQuery.data as ComponentBase[]) || [],
      isLoading: storageQuery.isLoading,
    },
  ];

  // Active slot config for modal
  const currentActiveConfig = slotConfigs.find((c) => c.type === activeModal);

  // Store actions helpers
  const handleSelect = (type: ComponentType, item: ComponentBase) => {
    if (typeof store.setComponent === 'function') {
      store.setComponent(type, item as any);
    } else {
      const setterName = `set${type.charAt(0).toUpperCase() + type.slice(1)}`;
      if (typeof (store as any)[setterName] === 'function') {
        (store as any)[setterName](item);
      }
    }
  };

  const handleRemove = (type: ComponentType) => {
    if (typeof store.removeComponent === 'function') {
      store.removeComponent(type);
    } else {
      const removerName = `remove${type.charAt(0).toUpperCase() + type.slice(1)}`;
      if (typeof (store as any)[removerName] === 'function') {
        (store as any)[removerName]();
      } else {
        const setterName = `set${type.charAt(0).toUpperCase() + type.slice(1)}`;
        if (typeof (store as any)[setterName] === 'function') {
          (store as any)[setterName](null);
        }
      }
    }
  };

  const handleClearBuild = () => {
    if (typeof store.clearBuild === 'function') {
      store.clearBuild();
    } else {
      slotConfigs.forEach((slot) => handleRemove(slot.type));
    }
    validateBuildMutation.reset();
  };

  // Total price calculation
  const totalPrice = typeof store.getTotalPrice === 'function'
    ? store.getTotalPrice()
    : slotConfigs.reduce((sum, slot) => sum + (Number(slot.component?.price) || 0), 0);

  const formattedTotalPrice = Number(totalPrice || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  const selectedCount = slotConfigs.filter((s) => s.component !== null).length;

  const handleValidateBuild = () => {
    if (!cpu || !motherboard || !ram || !pcCase || !psu) {
      // Still trigger mutation with present ids or let backend validate
    }

    validateBuildMutation.mutate({
      cpu_id: cpu?.id,
      motherboard_id: motherboard?.id,
      ram_id: ram?.id,
      gpu_id: gpu?.id ?? null,
      case_id: pcCase?.id,
      psu_id: psu?.id,
      cooler_id: cooler?.id ?? null,
    } as any);
  };

  const report = validateBuildMutation.data;

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 800 }} gutterBottom color="text.primary">
          Custom PC Builder
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configure and validate your custom PC components for complete hardware compatibility.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Left Area: 8 Component Slot Cards & Validation Section */}
        <Grid size={{ xs: 12, lg: 8 }}>
          <Grid container spacing={2}>
            {slotConfigs.map((slot) => (
              <Grid size={{ xs: 12, sm: 6 }} key={slot.type}>
                <ComponentSlot
                  label={slot.label}
                  icon={slot.icon}
                  component={slot.component}
                  onSelect={() => setActiveModal(slot.type)}
                  onRemove={() => handleRemove(slot.type)}
                />
              </Grid>
            ))}
          </Grid>

          {/* Validation Action and Feedback */}
          <Paper
            elevation={2}
            sx={{
              mt: 3,
              p: 3,
              backgroundColor: '#1e1e1e',
              borderRadius: 2,
              border: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Compatibility Check
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Check sockets, physical clearances, power requirements, and memory compatibility.
                </Typography>
              </Box>
              <Button
                variant="contained"
                size="large"
                color="primary"
                onClick={handleValidateBuild}
                disabled={validateBuildMutation.isPending || !cpu || !motherboard || !ram || !pcCase || !psu}
                startIcon={
                  validateBuildMutation.isPending ? (
                    <CircularProgress size={20} color="inherit" />
                  ) : (
                    <CheckCircleIcon />
                  )
                }
                sx={{
                  fontWeight: 700,
                  px: 3,
                  py: 1.2,
                  borderRadius: 2,
                }}
              >
                {validateBuildMutation.isPending ? 'Validating...' : 'Validate Build'}
              </Button>
            </Box>

            {/* Validation Mutation Error */}
            {validateBuildMutation.isError && (
              <Alert severity="error" variant="filled" sx={{ mt: 2.5, borderRadius: 2 }}>
                <AlertTitle>Validation Failed</AlertTitle>
                {(() => {
                  const detail = (validateBuildMutation.error as any)?.response?.data?.detail;
                  if (Array.isArray(detail)) {
                    // Pydantic 422 validation error
                    return detail.map((err, i) => <div key={i}>{err.msg}</div>);
                  }
                  if (typeof detail === 'string') {
                    return detail;
                  }
                  return (validateBuildMutation.error as Error)?.message || 'An error occurred during build validation. Please check that all required parts are selected.';
                })()}
              </Alert>
            )}

            {/* Compatibility Report Feedback */}
            {report && (
              <Stack spacing={2} sx={{ mt: 2.5 }}>
                {report.is_compatible && (!report.errors || report.errors.length === 0) && (
                  <Alert severity="success" variant="filled" sx={{ borderRadius: 2 }}>
                    <AlertTitle sx={{ fontWeight: 700 }}>Build is 100% Compatible!</AlertTitle>
                    All selected hardware components are fully compatible and ready for assembly.
                  </Alert>
                )}

                {report.errors && report.errors.length > 0 && (
                  <Alert severity="error" variant="filled" sx={{ borderRadius: 2 }}>
                    <AlertTitle sx={{ fontWeight: 700 }}>
                      Compatibility Errors ({report.errors.length})
                    </AlertTitle>
                    <Box component="ul" sx={{ m: 0, pl: 2.5 }}>
                      {report.errors.map((err, idx) => (
                        <li key={idx}>
                          <Typography variant="body2">{err}</Typography>
                        </li>
                      ))}
                    </Box>
                  </Alert>
                )}

                {report.warnings && report.warnings.length > 0 && (
                  <Alert severity="warning" variant="filled" sx={{ borderRadius: 2 }}>
                    <AlertTitle sx={{ fontWeight: 700 }}>
                      Compatibility Warnings ({report.warnings.length})
                    </AlertTitle>
                    <Box component="ul" sx={{ m: 0, pl: 2.5 }}>
                      {report.warnings.map((warn, idx) => (
                        <li key={idx}>
                          <Typography variant="body2">{warn}</Typography>
                        </li>
                      ))}
                    </Box>
                  </Alert>
                )}
              </Stack>
            )}
          </Paper>
        </Grid>

        {/* Right Area: Build Summary Panel */}
        <Grid size={{ xs: 12, lg: 4 }}>
          <Card
            elevation={2}
            sx={{
              backgroundColor: '#1e1e1e',
              borderRadius: 2,
              border: '1px solid rgba(255, 255, 255, 0.1)',
              position: { lg: 'sticky' },
              top: 24,
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Build Summary
                </Typography>
                <Chip
                  label={`${selectedCount} / ${slotConfigs.length} selected`}
                  size="small"
                  color={selectedCount === slotConfigs.length ? 'success' : 'default'}
                  variant="outlined"
                />
              </Box>

              <Divider sx={{ my: 1.5, borderColor: 'rgba(255, 255, 255, 0.08)' }} />

              <Stack spacing={1.5} sx={{ my: 2 }}>
                {slotConfigs.map((slot) => (
                  <Box
                    key={slot.type}
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      py: 0.5,
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, overflow: 'hidden', mr: 1 }}>
                      <Box sx={{ color: 'text.secondary', display: 'flex' }}>{slot.icon}</Box>
                      <Box sx={{ overflow: 'hidden' }}>
                        <Typography variant="body2" sx={{ fontWeight: 600 }} noWrap>
                          {slot.label}
                        </Typography>
                        <Typography
                          variant="caption"
                          color={slot.component ? 'text.secondary' : 'text.disabled'}
                          noWrap
                          sx={{ display: 'block' }}
                        >
                          {slot.component ? slot.component.name : 'Not selected'}
                        </Typography>
                      </Box>
                    </Box>

                    <Typography
                      variant="body2"
                      color={slot.component ? 'primary.light' : 'text.disabled'}
                      sx={{ whiteSpace: 'nowrap', fontWeight: slot.component ? 700 : 400 }}
                    >
                      {slot.component
                        ? `${Number(slot.component.price || 0).toFixed(2)} zł`
                        : '—'}
                    </Typography>
                  </Box>
                ))}
              </Stack>

              <WattageCalculator cpu={cpu} gpu={gpu} psu={psu} />

              <Divider sx={{ my: 2, borderColor: 'rgba(255, 255, 255, 0.12)' }} />

              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', my: 2 }}>
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Total Price:
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 800 }} color="primary.main">
                  {formattedTotalPrice} zł
                </Typography>
              </Box>

              <Stack spacing={1.5} sx={{ mt: 3 }}>
                <Button
                  fullWidth
                  variant="contained"
                  color="primary"
                  size="large"
                  onClick={handleValidateBuild}
                  disabled={validateBuildMutation.isPending || !cpu || !motherboard || !ram || !pcCase || !psu}
                  startIcon={
                    validateBuildMutation.isPending ? (
                      <CircularProgress size={20} color="inherit" />
                    ) : (
                      <CheckCircleIcon />
                    )
                  }
                  sx={{ fontWeight: 700, py: 1.2, borderRadius: 2 }}
                >
                  Validate Build
                </Button>

                {selectedCount > 0 && (
                  <Button
                    fullWidth
                    variant="outlined"
                    color="inherit"
                    onClick={handleClearBuild}
                    startIcon={<RestartAltIcon />}
                    sx={{
                      borderColor: 'rgba(255, 255, 255, 0.2)',
                      color: 'text.secondary',
                      '&:hover': {
                        borderColor: 'error.main',
                        color: 'error.main',
                      },
                    }}
                  >
                    Clear All Components
                  </Button>
                )}

                <ShareBuildButton
                  buildIds={{
                    cpu: cpu?.id,
                    motherboard: motherboard?.id,
                    ram: ram?.id,
                    gpu: gpu?.id,
                    psu: psu?.id,
                    case: pcCase?.id,
                    cooler: cooler?.id,
                    storage: storage?.id,
                  }}
                  disabled={selectedCount === 0}
                />

                <ExportBuildPDF
                  components={slotConfigs.map((s) => ({ label: s.label, component: s.component }))}
                  totalPrice={totalPrice}
                  disabled={selectedCount === 0}
                />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Selection Modal */}
      {currentActiveConfig && (
        <SelectionModal
          open={activeModal !== null}
          onClose={() => setActiveModal(null)}
          title={currentActiveConfig.modalTitle}
          items={currentActiveConfig.items}
          isLoading={currentActiveConfig.isLoading}
          onSelect={(item) => handleSelect(currentActiveConfig.type, item)}
        />
      )}
    </Container>
  );
};

export default BuilderPage;
