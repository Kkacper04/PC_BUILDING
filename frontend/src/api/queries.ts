import { useQuery, useMutation, type UseQueryOptions, type UseMutationOptions } from '@tanstack/react-query';
import apiClient from './client';
import type {
  CPUResponse,
  GPUResponse,
  MotherboardResponse,
  RAMResponse,
  PSUResponse,
  CaseResponse,
  StorageResponse,
  CPUCoolerResponse,
  BuildValidationRequest,
  CompatibilityReport,
  SSDRecommendation,
  CPUQueryParams,
  GPUQueryParams,
  MotherboardQueryParams,
  RAMQueryParams,
  PSUQueryParams,
  CaseQueryParams,
  CoolerQueryParams,
  StorageQueryParams,
  SSDRecommendParams,
} from '../types/api';

// ----------------------------------------------------------------------
// API Fetch Functions
// ----------------------------------------------------------------------

export const fetchCPUs = async (params?: CPUQueryParams): Promise<CPUResponse[]> => {
  const response = await apiClient.get<CPUResponse[]>('/cpus', { params });
  return response.data;
};

export const fetchCPU = async (id: number): Promise<CPUResponse> => {
  const response = await apiClient.get<CPUResponse>(`/cpus/${id}`);
  return response.data;
};

export const fetchGPUs = async (params?: GPUQueryParams): Promise<GPUResponse[]> => {
  const response = await apiClient.get<GPUResponse[]>('/gpus', { params });
  return response.data;
};

export const fetchGPU = async (id: number): Promise<GPUResponse> => {
  const response = await apiClient.get<GPUResponse>(`/gpus/${id}`);
  return response.data;
};

export const fetchMotherboards = async (params?: MotherboardQueryParams): Promise<MotherboardResponse[]> => {
  const response = await apiClient.get<MotherboardResponse[]>('/motherboards', { params });
  return response.data;
};

export const fetchMotherboard = async (id: number): Promise<MotherboardResponse> => {
  const response = await apiClient.get<MotherboardResponse>(`/motherboards/${id}`);
  return response.data;
};

export const fetchRAM = async (params?: RAMQueryParams): Promise<RAMResponse[]> => {
  const response = await apiClient.get<RAMResponse[]>('/ram', { params });
  return response.data;
};

export const fetchRAMItem = async (id: number): Promise<RAMResponse> => {
  const response = await apiClient.get<RAMResponse>(`/ram/${id}`);
  return response.data;
};

export const fetchPSUs = async (params?: PSUQueryParams): Promise<PSUResponse[]> => {
  const response = await apiClient.get<PSUResponse[]>('/psus', { params });
  return response.data;
};

export const fetchPSU = async (id: number): Promise<PSUResponse> => {
  const response = await apiClient.get<PSUResponse>(`/psus/${id}`);
  return response.data;
};

export const fetchCases = async (params?: CaseQueryParams): Promise<CaseResponse[]> => {
  const response = await apiClient.get<CaseResponse[]>('/cases', { params });
  return response.data;
};

export const fetchCase = async (id: number): Promise<CaseResponse> => {
  const response = await apiClient.get<CaseResponse>(`/cases/${id}`);
  return response.data;
};

export const fetchCoolers = async (params?: CoolerQueryParams): Promise<CPUCoolerResponse[]> => {
  const response = await apiClient.get<CPUCoolerResponse[]>('/coolers', { params });
  return response.data;
};

export const fetchCooler = async (id: number): Promise<CPUCoolerResponse> => {
  const response = await apiClient.get<CPUCoolerResponse>(`/coolers/${id}`);
  return response.data;
};

export const fetchStorage = async (params?: StorageQueryParams): Promise<StorageResponse[]> => {
  const response = await apiClient.get<StorageResponse[]>('/storage', { params });
  return response.data;
};

export const fetchStorageItem = async (id: number): Promise<StorageResponse> => {
  const response = await apiClient.get<StorageResponse>(`/storage/${id}`);
  return response.data;
};

export const validateBuild = async (data: BuildValidationRequest): Promise<CompatibilityReport> => {
  const response = await apiClient.post<CompatibilityReport>('/build/validate', data);
  return response.data;
};

export const fetchSSDRecommendation = async (params?: SSDRecommendParams): Promise<SSDRecommendation> => {
  const response = await apiClient.get<SSDRecommendation>('/build/recommend-ssd', { params });
  return response.data;
};

// ----------------------------------------------------------------------
// React Query Hooks
// ----------------------------------------------------------------------

export const useCPUs = (
  params?: CPUQueryParams,
  options?: Omit<UseQueryOptions<CPUResponse[], Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<CPUResponse[], Error>({
    queryKey: ['cpus', params],
    queryFn: () => fetchCPUs(params),
    ...options,
  });
};

export const useCPU = (
  id: number,
  options?: Omit<UseQueryOptions<CPUResponse, Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<CPUResponse, Error>({
    queryKey: ['cpus', id],
    queryFn: () => fetchCPU(id),
    enabled: Boolean(id),
    ...options,
  });
};

export const useGPUs = (
  params?: GPUQueryParams,
  options?: Omit<UseQueryOptions<GPUResponse[], Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<GPUResponse[], Error>({
    queryKey: ['gpus', params],
    queryFn: () => fetchGPUs(params),
    ...options,
  });
};

export const useGPU = (
  id: number,
  options?: Omit<UseQueryOptions<GPUResponse, Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<GPUResponse, Error>({
    queryKey: ['gpus', id],
    queryFn: () => fetchGPU(id),
    enabled: Boolean(id),
    ...options,
  });
};

export const useMotherboards = (
  params?: MotherboardQueryParams,
  options?: Omit<UseQueryOptions<MotherboardResponse[], Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<MotherboardResponse[], Error>({
    queryKey: ['motherboards', params],
    queryFn: () => fetchMotherboards(params),
    ...options,
  });
};

export const useMotherboard = (
  id: number,
  options?: Omit<UseQueryOptions<MotherboardResponse, Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<MotherboardResponse, Error>({
    queryKey: ['motherboards', id],
    queryFn: () => fetchMotherboard(id),
    enabled: Boolean(id),
    ...options,
  });
};

export const useRAM = (
  params?: RAMQueryParams,
  options?: Omit<UseQueryOptions<RAMResponse[], Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<RAMResponse[], Error>({
    queryKey: ['ram', params],
    queryFn: () => fetchRAM(params),
    ...options,
  });
};

export const useRAMItem = (
  id: number,
  options?: Omit<UseQueryOptions<RAMResponse, Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<RAMResponse, Error>({
    queryKey: ['ram', id],
    queryFn: () => fetchRAMItem(id),
    enabled: Boolean(id),
    ...options,
  });
};

export const usePSUs = (
  params?: PSUQueryParams,
  options?: Omit<UseQueryOptions<PSUResponse[], Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<PSUResponse[], Error>({
    queryKey: ['psus', params],
    queryFn: () => fetchPSUs(params),
    ...options,
  });
};

export const usePSU = (
  id: number,
  options?: Omit<UseQueryOptions<PSUResponse, Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<PSUResponse, Error>({
    queryKey: ['psus', id],
    queryFn: () => fetchPSU(id),
    enabled: Boolean(id),
    ...options,
  });
};

export const useCases = (
  params?: CaseQueryParams,
  options?: Omit<UseQueryOptions<CaseResponse[], Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<CaseResponse[], Error>({
    queryKey: ['cases', params],
    queryFn: () => fetchCases(params),
    ...options,
  });
};

export const useCase = (
  id: number,
  options?: Omit<UseQueryOptions<CaseResponse, Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<CaseResponse, Error>({
    queryKey: ['cases', id],
    queryFn: () => fetchCase(id),
    enabled: Boolean(id),
    ...options,
  });
};

export const useCoolers = (
  params?: CoolerQueryParams,
  options?: Omit<UseQueryOptions<CPUCoolerResponse[], Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<CPUCoolerResponse[], Error>({
    queryKey: ['coolers', params],
    queryFn: () => fetchCoolers(params),
    ...options,
  });
};

export const useCooler = (
  id: number,
  options?: Omit<UseQueryOptions<CPUCoolerResponse, Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<CPUCoolerResponse, Error>({
    queryKey: ['coolers', id],
    queryFn: () => fetchCooler(id),
    enabled: Boolean(id),
    ...options,
  });
};

export const useStorage = (
  params?: StorageQueryParams,
  options?: Omit<UseQueryOptions<StorageResponse[], Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<StorageResponse[], Error>({
    queryKey: ['storage', params],
    queryFn: () => fetchStorage(params),
    ...options,
  });
};

export const useStorageItem = (
  id: number,
  options?: Omit<UseQueryOptions<StorageResponse, Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<StorageResponse, Error>({
    queryKey: ['storage', id],
    queryFn: () => fetchStorageItem(id),
    enabled: Boolean(id),
    ...options,
  });
};

export const useValidateBuild = (
  options?: UseMutationOptions<CompatibilityReport, Error, BuildValidationRequest>
) => {
  return useMutation<CompatibilityReport, Error, BuildValidationRequest>({
    mutationFn: validateBuild,
    ...options,
  });
};

export const useSSDRecommendation = (
  params?: SSDRecommendParams,
  options?: Omit<UseQueryOptions<SSDRecommendation, Error>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<SSDRecommendation, Error>({
    queryKey: ['recommend-ssd', params],
    queryFn: () => fetchSSDRecommendation(params),
    ...options,
  });
};
