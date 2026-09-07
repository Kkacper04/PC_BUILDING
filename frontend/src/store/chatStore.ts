import { create } from 'zustand';
import type { ChatMessage } from '../types/api';

interface ChatState {
  isOpen: boolean;
  messages: ChatMessage[];
  isLoading: boolean;
  
  toggleChat: () => void;
  addMessage: (msg: ChatMessage) => void;
  setLoading: (loading: boolean) => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  isOpen: false,
  messages: [
    { role: 'assistant', content: 'Welcome to the PC Builder. Describe your ideal PC build, including your budget and primary use case (e.g., gaming, video editing, office work), and I will generate a fully compatible parts list for you.' }
  ],
  isLoading: false,
  
  toggleChat: () => set((state) => ({ isOpen: !state.isOpen })),
  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  setLoading: (loading) => set({ isLoading: loading }),
  clearChat: () => set({ 
    messages: [{ role: 'assistant', content: 'Welcome to the PC Builder. Describe your ideal PC build, including your budget and primary use case (e.g., gaming, video editing, office work), and I will generate a fully compatible parts list for you.' }] 
  }),
}));
