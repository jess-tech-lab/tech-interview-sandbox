import * as Haptics from 'expo-haptics';
export function useHaptics() { const tap = () => { Haptics.selectionAsync().catch(() => undefined); }; const success = () => { Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success).catch(() => undefined); }; return { tap, success }; }
