import { create } from 'zustand';
import type { ChatMessage } from '../types/api';

const WELCOME_MESSAGE: ChatMessage = {
  role: 'assistant',
  content: 'Welcome to the PC Builder. Describe your ideal PC build, including your budget and primary use case (e.g., gaming, video editing, office work), and I will generate a fully compatible parts list for you.'
};

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
  messages: [WELCOME_MESSAGE],
  isLoading: false,
  
  toggleChat: () => set((state) => ({ isOpen: !state.isOpen })),
  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  setLoading: (loading) => set({ isLoading: loading }),
  clearChat: () => set({ messages: [WELCOME_MESSAGE] }),
}));
